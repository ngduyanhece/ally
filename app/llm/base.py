from abc import abstractmethod
from typing import AsyncIterable, ClassVar, List

from langchain.callbacks.streaming_aiter import AsyncIteratorCallbackHandler
from pydantic import BaseModel

from app.core.settings import settings
from app.logger import get_logger

logger = get_logger(__name__)

class LLMBase(BaseModel):
    """
    Base class for LLM brain models.
    """
    brain_settings: ClassVar = settings
    model: str = None
    temperature: float = 0.1
    chat_id: str = None
    brain_id: str = None
    max_tokens: int = 256
    user_openai_api_key: str = None
    streaming: bool = False
    openai_api_key: str = None
    prompt_id: str = None
    callbacks: List[
        AsyncIteratorCallbackHandler
    ] = None

    def _determine_api_key(self, openai_api_key, user_openai_api_key):
        """If user provided an API key, use it."""
        if user_openai_api_key is not None:
            return user_openai_api_key
        else:
            return openai_api_key
    
    def _determine_streaming(self, model: str, streaming: bool) -> bool:
        """If the model name allows for streaming and streaming is declared, set streaming to True."""
        return streaming
    
    def _determine_callback_array(
        self, streaming
    ) -> List[AsyncIteratorCallbackHandler]: 
        """If streaming is set, set the AsyncIteratorCallbackHandler as the only callback."""
        if streaming:
            return [
                AsyncIteratorCallbackHandler()
            ]
        
    def __init__(self, **data):
        super().__init__(**data)

        self.openai_api_key = self._determine_api_key(
            self.brain_settings.openai_api_key, self.user_openai_api_key
        )
        self.streaming = self._determine_streaming(
            self.model, self.streaming
        ) 
        self.callbacks = self._determine_callback_array(
            self.streaming
        )
    
    class Config:
        """Configuration of the Pydantic Object"""

        # Allowing arbitrary types for class validation
        arbitrary_types_allowed = True

        # the below methods define the names, arguments and return types for the most useful functions for the child classes. These should be overwritten if they are used.
        @abstractmethod
        def generate_answer(self, text_input: str) -> str:
            """
            Generate an answer to a given question using QA Chain.
            :param question: The question
            :return: The generated answer.

            This function should also call: _create_qa, get_chat_history and format_chat_history.
            It should also update the chat_history in the DB.
            """

        @abstractmethod
        async def generate_stream(self, question: str) -> AsyncIterable:
            """
            Generate a streaming answer to a given question using QA Chain.
            :param question: The question
            :return: An async iterable which generates the answer.

            This function has to do some other things:
            - Update the chat history in the DB with the chat details(chat_id, question) -> Return a message_id and timestamp
            - Use the _acall_chain method inside create_task from asyncio to run the process on a child thread.
            - Append each token to the chat_history object from the db and yield it from the function
            - Append each token from the callback to an answer string -> Used to update chat history in DB (update_message_by_id)
            """
            raise NotImplementedError(
                "Async generation not implemented for this BrainPicking Class."
            )
