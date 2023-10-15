from typing import Optional
from uuid import UUID

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
from app.repository.chat.format_chat_history import format_chat_history
from app.repository.chat.get_chat_history import (GetChatHistoryOutput,
                                                  get_chat_history)
from app.repository.chat.update_chat_history import update_chat_history
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
                    "question": chat_input.chat_input,
                    "chat_history": "",
                }
            )
        answer = model_response["answer"]
        new_chat = update_chat_history(
            CreateChatHistory(
                **{
                    "chat_id": chat_id,
                    "user_message": chat_input.chat_input,
                    "assistant": answer,
                    "brain_id": chat_input.brain_id,
                    "prompt_id": self.prompt_to_use_id,
                }
            )
        )

        if chat_input.brain_id:
            brain = get_brain_by_id(chat_input.brain_id)
        else:
            brain = get_brain_by_id(self.brain_id)

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
