from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from ally.modules.knowledge.dto.outputs import DeleteKnowledgeResponse
from app.modules.knowledge.entity.knowledge import (CreateKnowledgeProperties,
                                                    KnowledgeEntity)


class KnowledgeInterface(ABC):
	@abstractmethod
	def insert_knowledge(
		self, knowledge: CreateKnowledgeProperties
	) -> KnowledgeEntity:
		"""
		Add a knowledge
		"""
		pass
	
	@abstractmethod
	def remove_knowledge_by_id(
		self,
		knowledge_id: UUID,
	) -> DeleteKnowledgeResponse:
		"""
		Args:
			knowledge_id (UUID): The id of the knowledge
		Returns:
			str: Status message
		"""
		pass

	@abstractmethod
	def get_knowledge_by_id(self, knowledge_id: UUID) -> KnowledgeEntity:
		"""
		Get a knowledge by its id
		Args:
			knowledge_id (UUID): The id of the knowledge_id
		"""
		pass

	@abstractmethod
	def update_knowledge_property_by_id(
			self, knowledge_id: UUID, property: dict) -> KnowledgeEntity:
		"""
		Update a knowledge property by its id
		Args:
			knowledge_id (UUID): The id of the knowledge
			value: The value to update
		"""
		pass

	@abstractmethod
	def get_all_knowledge_in_agent(self, agent_id: str) -> List[KnowledgeEntity]:
		"""
		Get all the knowledge in an agent
		Args:
		agent_id (UUID): The id of an agent
		"""
		pass

	@abstractmethod
	def remove_agent_all_knowledge(self, agent_id: str) -> None:
		"""
		Remove all knowledge in an agent
		Args:
			agent_id (str): The id of the agent
		"""
		pass
