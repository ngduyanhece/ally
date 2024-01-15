from abc import ABC, abstractmethod
from typing import List

from modules.agent.entity.agent_entity import ToolEntity


class AgentToolInterface(ABC):
	@abstractmethod
	def get_tools_for_agent(
		self,
		agent_id: str
	) -> List[ToolEntity]:
		"""
		get all tools for a agent
		"""
		pass