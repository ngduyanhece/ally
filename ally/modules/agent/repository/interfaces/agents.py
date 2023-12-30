from abc import ABC, abstractmethod

from ally.modules.agent.dto.inputs import (AgentUpdatableProperties,
                                           CreateAgentProperties)
from ally.modules.agent.entity.agent_entity import AgentEntity


class AgentsInterface(ABC):
	@abstractmethod
	def create_agent(self, agent: CreateAgentProperties) -> AgentEntity:
		"""
		Create a agent
		"""
		pass

	@abstractmethod
	def update_agent_last_update_time(self, agent_id: str) -> None:
		"""
		Update the last update time of the agent
		"""
		pass

	@abstractmethod
	def delete_agent(self, agent_id: str):
		"""
		Delete an agent
		"""
		pass

	@abstractmethod
	def update_agent_by_id(
		self, agent_id: str, agent: AgentUpdatableProperties
	) -> AgentEntity | None:
		"""
		Update an agent by id
		"""
		pass

	@abstractmethod
	def get_agent_by_id(self, agent_id: str) -> AgentEntity | None:
		"""
		Get an agent by id
		"""
		pass

	@abstractmethod
	def get_agent_by_name(self, agent_name: str) -> AgentEntity | None:
		"""
		Get an agent by name
		"""
		pass
