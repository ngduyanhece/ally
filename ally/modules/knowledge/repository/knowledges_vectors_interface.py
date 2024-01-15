from abc import ABC, abstractmethod
from typing import List
from uuid import UUID


class KnowledgesVectorsInterface(ABC):
	@abstractmethod
	def create_agent_vector(self, agent_id, vector_id, file_sha1):
		"""
		Create an agent vector
		"""
		pass

	@abstractmethod
	def get_vector_ids_from_file_sha1(self, file_sha1: str):
		"""
		Get vector ids from file sha1
		"""
		pass

	@abstractmethod
	def get_agent_vector_ids(self, agent_id) -> List[UUID]:
		"""
		Get agent vector ids
		"""
		pass

	@abstractmethod
	def delete_file_from_agent(self, agent_id, file_name: str):
		"""
		Delete file from agent
		"""
		pass

	@abstractmethod
	def delete_agent_vector(self, agent_id: str):
		"""
		Delete agent vector
		"""
		pass
