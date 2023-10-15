from typing import Any, ClassVar, Dict, List
from uuid import UUID

from langchain.agents import AgentType, Tool, initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.llms.base import BaseLLM
from pydantic import BaseModel

from app.core.settings import settings
from app.models.chats import MetaChatInput


class LLMMetaBrain(BaseModel):
    meta_brain_settings: ClassVar = settings
    model: str = None
    temperature: float = 0.1
    chat_id: str = None
    meta_brain_id: str = None
    max_tokens: int = 256
    user_openai_api_key: str = None
    openai_api_key: str = None
    brains_infos: List[Dict[str, Any]] = None

    def _determine_api_key(self, openai_api_key, user_openai_api_key):
        """If user provided an API key, use it."""
        if user_openai_api_key is not None:
            return user_openai_api_key
        else:
            return openai_api_key
    
    def __init__(self, **data):
        super().__init__(**data)

        self.openai_api_key = self._determine_api_key(
            self.brain_settings.openai_api_key, self.user_openai_api_key
        )
    
    class Config:
        """Configuration of the Pydantic Object"""

        # Allowing arbitrary types for class validation
        arbitrary_types_allowed = True

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
    
    def _create_tools(self):
        tools = []
        for brain_info in self.brains_infos:
            tools.append(
                Tool.from_function(
                    func=brain_info["tool"](
                        **brain_info["tool_config"]).generate_answer,
                    name=brain_info["name"],
                    description=brain_info["description"],
                    args_schema=brain_info["args_schema"],
                )
            )
        return tools

    def _create_policy(self):
        llm = self._create_llm(
            model=self.model,
            temperature=self.temperature,  # type: ignore
            max_tokens=self.max_tokens,
        )
        tools = self._create_tools()
        agent = initialize_agent(
            tools, llm, agent=AgentType.OPENAI_MULTI_FUNCTIONS
        )
        return agent
    
    def generate_answer(
        self, chat_id: UUID,
        chat_input: MetaChatInput
    ) -> Dict[str, Any]:
        agent_policy = self._create_policy()
        answer = agent_policy(
            {
                "input": chat_input.chat_input,
            }
        )
        return answer
