from uuid import UUID

from pydantic import BaseModel

from app.llm.llm_brain import LLMBrain
from app.llm.llm_user_simulator import LLMUserSimulator
from app.logger import get_logger
from app.models.chats import ChatInput
from app.repository.chat.create_chat import CreateChatProperties, create_chat
from app.repository.task_goal.get_task_goals_by_brain_id import \
    get_task_goals_by_brain_id

logger = get_logger(__name__)

class UserSimulatorBench(BaseModel):
	llm_brain: LLMBrain
	llm_user_simulator: LLMUserSimulator
	user_id: UUID
	max_turns: int = 10

	def simulate(self):
		"""
		Simulate a conversation between the user and the assistant.
		"""
		task_goals = get_task_goals_by_brain_id(
			brain_id=self.llm_user_simulator.brain_id)
		for task_goal in task_goals:
			logger.info(f"Start Simulate for Task goal: {task_goal.title}")
			self.llm_user_simulator.goal = task_goal
			user_simulator_chat = create_chat(
				user_id=self.user_id,
				chat_data=CreateChatProperties(name=f"USER_SIMULATOR: {task_goal.title}")
			)
			system_chat = create_chat(
				user_id=self.user_id,
				chat_data=CreateChatProperties(name=f"SYSTEM: {task_goal.title}")
			)
			system_msg = "[START]]"
			
			while not self.llm_user_simulator.is_terminated and self.max_turns > 0:
				user_simulator_msg = self.llm_user_simulator.generate_answer(
					chat_id=user_simulator_chat["chat_id"],
					chat_input=ChatInput(
						chat_input=system_msg,
						use_history=True,
						model=None,
						temperature=None,
						max_tokens=None,
						brain_id=None,
						prompt_id=None,
					)
				)
				system_msg_history_output = self.llm_brain.generate_answer(
					chat_id=system_chat["chat_id"],
					chat_input=ChatInput(
						chat_input=user_simulator_msg.assistant,
						use_history=True,
						model=None,
						temperature=None,
						max_tokens=None,
						brain_id=None,
						prompt_id=None,
					)
				)
				system_msg = system_msg_history_output.assistant
				self.max_turns -= 1
