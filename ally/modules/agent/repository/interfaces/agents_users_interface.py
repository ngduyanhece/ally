from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from ally.modules.agent.entity.agent_entity import AgentUser, UserAgentEntity


class AgentUserInterface(ABC):
	
	@abstractmethod
	def get_user_agents(
		self,
		user_id: UUID
	) -> list[UserAgentEntity]:
		"""
		get all agents for a user
		"""
		pass

	@abstractmethod
	def get_agent_for_user(
		self,
		user_id: UUID,
		agent_id: str
	) -> UserAgentEntity:
		"""
		get a specific agent for a user
		"""
		pass

	@abstractmethod
	def delete_agent_user_by_id(
		self,
		user_id: UUID,
		agent_id: str
	):
		"""
		delete a specific agent for a user
		"""
		pass

	@abstractmethod
	def delete_agent_users(self, agent_id: str):
		"""
		Delete all users for a agent
		"""
		pass

	@abstractmethod
	def create_agent_user(
		self,
		user_id: UUID,
		agent_id: str,
		rights
	):
		"""
		Create a agent user
		"""
		pass

	@abstractmethod
	def get_agent_users(self, agent_id: str) -> List[AgentUser]:
		"""
		Get all users for an agent
		"""
		pass

