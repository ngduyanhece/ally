import asyncio
from typing import AsyncIterable, Awaitable, Optional
from uuid import UUID

from langchain.callbacks.streaming_aiter import AsyncIteratorCallbackHandler
from langchain.chains import ConversationalRetrievalChain, LLMChain
from langchain.chains.question_answering import load_qa_chain
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.llms.base import BaseLLM
from langchain.prompts.chat import (ChatPromptTemplate,
                                    HumanMessagePromptTemplate,
                                    SystemMessagePromptTemplate)
from supabase.client import Client, create_client

from app.llm.base import LLMBase
from app.llm.default_prompts.CONDENSE_PROMPT import CONDENSE_QUESTION_PROMPT
from app.llm.utils.get_prompt_to_use import get_prompt_to_use
from app.llm.utils.get_prompt_to_use_id import get_prompt_to_use_id
from app.logger import get_logger
from app.models.chats import ChatInput
from app.models.databases.supabase.chats import CreateChatHistory
from app.repository.brain.get_brain_by_id import get_brain_by_id
from app.repository.brain.get_question_context_from_brain import \
    get_question_context_from_brain
from app.repository.chat.format_chat_history import format_chat_history
from app.repository.chat.get_chat_history import (GetChatHistoryOutput,
                                                  get_chat_history)
from app.repository.chat.update_chat_history import update_chat_history
from app.repository.chat.update_message_by_id import update_message_by_id
from app.vectorstore.supabase import CustomSupabaseVectorStore

logger = get_logger(__name__)
ALLY_DEFAULT_PROMPT = "Your name is ally. You're a helpful assistant.  If you don't know the answer, just say that you don't know, don't try to make up an answer."

class LLMBrain(LLMBase):
    """
    Base class for the LLMBrain 
    """
    supabase_client: Optional[Client] = None
    vector_store: Optional[CustomSupabaseVectorStore] = None

    def __init__(
        self,
        model: str,
        brain_id: str,
        chat_id: str,
        prompt_id: str,
        streaming: bool = False,
        **kwargs,
    ):
        super().__init__(
            model=model,
            brain_id=brain_id,
            chat_id=chat_id,
            prompt_id=prompt_id,
            streaming=streaming,
            **kwargs,
        )
        self.supabase_client = self._create_supabase_client()
        self.vector_store = self._create_vector_store()
    
    @property
    def prompt_to_use(self):
        return get_prompt_to_use(UUID(self.brain_id), (self.prompt_id))

    @property
    def prompt_to_use_id(self) -> Optional[UUID]:
        return get_prompt_to_use_id(UUID(self.brain_id), self.prompt_id)
    
    @property
    def embeddings(self) -> OpenAIEmbeddings:
        return OpenAIEmbeddings(
            openai_api_key=self.openai_api_key
        )
    
    def _create_supabase_client(self) -> Client:
        return create_client(
            self.brain_settings.supabase_url,
            self.brain_settings.supabase_service_key
        )

    def _create_vector_store(self) -> CustomSupabaseVectorStore:
        return CustomSupabaseVectorStore(
            self.supabase_client,
            self.embeddings,
            table_name="vectors",
            brain_id=self.brain_id,
        )
    
    def _create_llm(
        self, model, temperature=0, streaming=False, callbacks=None, max_tokens=256
    ) -> BaseLLM:
        """
        Determine the language model to be used.
        :param model: Language model name to be used.
        :param streaming: Whether to enable streaming of the model
        :param callbacks: Callbacks to be used for streaming
        :return: Language model instance
        """
        return ChatOpenAI(
            temperature=temperature,
            max_tokens=max_tokens,
            model=model,
            streaming=streaming,
            verbose=False,
            callbacks=callbacks,
            openai_api_key=self.openai_api_key,
        )
    
    def _create_prompt_template(self):
        prompt_content = (
            self.prompt_to_use.content if self.prompt_to_use else ALLY_DEFAULT_PROMPT
        )

        messages = [
            SystemMessagePromptTemplate.from_template(prompt_content),
            HumanMessagePromptTemplate.from_template("{question}"),
        ]
        CHAT_PROMPT = ChatPromptTemplate.from_messages(messages)
        return CHAT_PROMPT
    
    def generate_answer(
        self, chat_id: UUID, chat_input: ChatInput
    ) -> GetChatHistoryOutput:
        transformed_history = format_chat_history(
            get_chat_history(self.chat_id))
        
        answering_llm = self._create_llm(
            model=self.model, streaming=False, callbacks=self.callbacks
        )

        doc_chain = load_qa_chain(
            answering_llm, chain_type="stuff",
            prompt=self._create_prompt_template()
        )
        qa = ConversationalRetrievalChain(
            retriever=self.vector_store.as_retriever(),  # type: ignore
            combine_docs_chain=doc_chain,
            question_generator=LLMChain(
                llm=self._create_llm(model=self.model),
                prompt=CONDENSE_QUESTION_PROMPT
            ),
            verbose=False,
            rephrase_question=False,
        )
        if chat_input.use_history:
            model_response = qa(
                {
                    "question": chat_input.chat_input,
                    "chat_history": transformed_history,
                }
            )
        else:
            model_response = qa(
                {
                    "question":chat_input.chat_input,
                    "chat_history": "",
                }
            )
        answer = model_response["answer"]

        if chat_input.brain_id:
            brain = get_brain_by_id(chat_input.brain_id)
        else:
            brain = get_brain_by_id(self.brain_id)

        new_chat = update_chat_history(
            CreateChatHistory(
                **{
                    "chat_id": chat_id,
                    "user_message": chat_input.chat_input,
                    "assistant": answer,
                    "brain_id": self.brain_id if self.brain_id
                    else chat_input.brain_id,
                    "prompt_id": self.prompt_to_use_id,
                    "context": get_question_context_from_brain(
                        brain.brain_id, chat_input.chat_input),
                }
            )
        )
        return GetChatHistoryOutput(
            **{
                "chat_id": chat_id,
                "user_message": chat_input.chat_input,
                "assistant": answer,
                "message_time": new_chat.message_time,
                "prompt_title": self.prompt_to_use.title
                if self.prompt_to_use
                else None,
                "brain_name": brain.name if brain else None,
                "message_id": new_chat.message_id,
            }
        )
    
    async def generate_answer_stream(
            self, chat_id: UUID, 
            chat_input: ChatInput
    ) -> AsyncIterable:
        history = get_chat_history(self.chat_id)
        callback = AsyncIteratorCallbackHandler()
        self.callbacks = [callback]

        answering_llm = self._create_llm(
            model=self.model, streaming=False, callbacks=self.callbacks
        )

        doc_chain = load_qa_chain(
            answering_llm, chain_type="stuff",
            prompt=self._create_prompt_template()
        )
        qa = ConversationalRetrievalChain(
            retriever=self.vector_store.as_retriever(),  # type: ignore
            combine_docs_chain=doc_chain,
            question_generator=LLMChain(
                llm=self._create_llm(model=self.model),
                prompt=CONDENSE_QUESTION_PROMPT
            ),
            verbose=False,
            rephrase_question=False,
        )
        transformed_history = format_chat_history(history)
        response_tokens = []

        async def wrap_done(fn: Awaitable, event: asyncio.Event):
            try:
                await fn
            except Exception as e:
                logger.error(f"Caught exception: {e}")
            finally:
                event.set()
        if chat_input.use_history:
            run = asyncio.create_task(
                wrap_done(
                    qa.acall(
                        {
                            "question": chat_input.chat_input,
                            "chat_history": transformed_history,
                        }
                    ),
                    callback.done,
                )
            )
        else:
            run = asyncio.create_task(
                wrap_done(
                    qa.acall(
                        {
                            "question": chat_input.chat_input,
                            "chat_history": "",
                        }
                    ),
                    callback.done,
                )
            )
        if chat_input.brain_id:
            brain = get_brain_by_id(chat_input.brain_id)
        else:
            brain = get_brain_by_id(self.brain_id)

        streamed_chat_history = update_chat_history(
            CreateChatHistory(
                **{
                    "chat_id": str(chat_id),
                    "user_message": chat_input.chat_input,
                    "assistant": "",
                    "brain_id": self.brain_id if self.brain_id else chat_input.brain_id,
                    "prompt_id": self.prompt_to_use_id,
                    "context": get_question_context_from_brain(
                        brain, chat_input.chat_input),
                }
            )
        )
        streamed_chat_history = GetChatHistoryOutput(
            **{
                "chat_id": str(chat_id),
                "message_id": streamed_chat_history.message_id,
                "message_time": streamed_chat_history.message_time,
                "user_message": chat_input.chat_input,
                "assistant": "",
                "prompt_title": self.prompt_to_use.title
                if self.prompt_to_use
                else None,
                "brain_name": brain.name if brain else None,
            }
        )
        async for token in callback.aiter():
            logger.info("Token: %s", token)
            response_tokens.append(token)
            streamed_chat_history.assistant = token
            yield f"data: {json.dumps(streamed_chat_history.dict())}"

        await run
        assistant = "".join(response_tokens)
        update_message_by_id(
            message_id=str(streamed_chat_history.message_id),
            user_message=chat_input.chat_input,
            assistant=assistant,
        )

    def agent_chat_interface(
        self, chat_input: str, use_history: bool = True
    ) -> GetChatHistoryOutput:
        transformed_history = format_chat_history(
            get_chat_history(self.chat_id))
        
        answering_llm = self._create_llm(
            model=self.model, streaming=False, callbacks=self.callbacks
        )

        doc_chain = load_qa_chain(
            answering_llm, chain_type="stuff",
            prompt=self._create_prompt_template()
        )
        qa = ConversationalRetrievalChain(
            retriever=self.vector_store.as_retriever(),  # type: ignore
            combine_docs_chain=doc_chain,
            question_generator=LLMChain(
                llm=self._create_llm(model=self.model),
                prompt=CONDENSE_QUESTION_PROMPT
            ),
            verbose=False,
            rephrase_question=False,
        )
        if (use_history):
            model_response = qa(
                {
                    "question": chat_input,
                    "chat_history": transformed_history,
                }
            )
        else:
            model_response = qa(
                {
                    "question": chat_input,
                    "chat_history": "",
                }
            )
        answer = model_response["answer"]
        new_chat = update_chat_history(
            CreateChatHistory(
                **{
                    "chat_id": self.chat_id,
                    "user_message": chat_input,
                    "assistant": answer,
                    "brain_id": self.brain_id,
                    "prompt_id": self.prompt_to_use_id,
                    "context": get_question_context_from_brain(
                        self.brain_id, chat_input),
                }
            )
        )

        brain = get_brain_by_id(self.brain_id)

        return GetChatHistoryOutput(
            **{
                "chat_id": self.chat_id,
                "user_message": chat_input,
                "assistant": answer,
                "message_time": new_chat.message_time,
                "prompt_title": self.prompt_to_use.title
                if self.prompt_to_use
                else None,
                "brain_name": brain.name,
                "message_id": new_chat.message_id,
            }
        )
