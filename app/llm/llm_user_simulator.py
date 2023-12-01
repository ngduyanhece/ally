from typing import ClassVar
from uuid import UUID

from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.llms.base import BaseLLM
from langchain.prompts.chat import (ChatPromptTemplate,
                                    HumanMessagePromptTemplate,
                                    SystemMessagePromptTemplate)
from pydantic import BaseModel

from app.core.settings import settings
from app.logger import get_logger
from app.models.brain_entity import BrainEntity
from app.models.chats import ChatInput
from app.models.databases.supabase.chats import CreateUserSimulatorChatHistory
from app.models.task_goal import TaskGoalEntity
from app.repository.chat.format_chat_history import format_chat_history
from app.repository.chat.get_chat_history import (GetChatHistoryOutput,
                                                  get_chat_history)
from app.repository.chat.update_user_simulator_chat_history import \
    update_user_simulator_chat_history
from app.repository.task_goal.update_task_goal_by_brain_id_goal_id import \
    update_task_goal_by_brain_id_goal_id

logger = get_logger(__name__)


class LLMUserSimulator(BaseModel):
	"""
	Base class for the LLM user simulator.
	"""
	class Config:
		arbitrary_types_allowed = True

	brain_settings: ClassVar = settings
	brain: BrainEntity
	user_openai_api_key: str = None
	goal: TaskGoalEntity = None
	is_terminated: bool = False

	def _create_llm(self, temperature, max_tokens, model, openai_api_key) -> BaseLLM:
		"""
		Determine the language model to be used.
		:param model: Language model name to be used.
		:return: Language model instance
		"""
		return ChatOpenAI(
				temperature=temperature,
				max_tokens=max_tokens,
				model=model,
				verbose=False,
				openai_api_key=openai_api_key,
		)
	
	def _create_prompt_template(self):
		messages = [
				SystemMessagePromptTemplate.from_template(self.goal.content),
				HumanMessagePromptTemplate.from_template("{chat_input}"),
		]
		CHAT_PROMPT = ChatPromptTemplate.from_messages(messages)
		return CHAT_PROMPT
	
	def generate_answer(
		self, chat_id: UUID, chat_input: ChatInput
	) -> GetChatHistoryOutput:
		transformed_history = format_chat_history(
			get_chat_history(chat_id))
		
		user_simulator = LLMChain(
			llm=self._create_llm(
				temperature=self.brain.temperature,
				max_tokens=self.brain.max_tokens,
				model=self.brain.model,
				openai_api_key=self.user_openai_api_key if self.user_openai_api_key is not None else self.brain.openai_api_key,
			),
			prompt=self._create_prompt_template(),
		)
		model_response = user_simulator(
			{
				"chat_input": chat_input.chat_input,
				"chat_history": transformed_history,
				"context": "",
			}
		)
		answer = model_response["text"]
		new_chat = update_user_simulator_chat_history(
			CreateUserSimulatorChatHistory(
				**{
					"chat_id": chat_id,
					"user_message": chat_input.chat_input,
					"assistant": answer,
					"task_goal": self.goal.content,
					"brain_id": self.brain.brain_id,
					"context": "",
				}
			)
		)
		if "[END]" in answer:
				self.is_terminated = True
				self.goal.goal_achieved = True
				_ = update_task_goal_by_brain_id_goal_id(
					brain_id=self.brain_id,
					goal_id=self.goal.id,
					task_goal=self.goal
				)
		elif "[STOP]" in answer:
				self.is_terminated = True

		return GetChatHistoryOutput(
			**{
				"chat_id": chat_id,
				"user_message": chat_input.chat_input,
				"assistant": answer,
				"message_time": new_chat.message_time,
				"prompt_title": None,
				"brain_name": None,
				"message_id": new_chat.message_id,
			}
		)
