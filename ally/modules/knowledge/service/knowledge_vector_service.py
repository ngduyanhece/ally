from typing import Any, List

from ally.logger import get_logger
from ally.modules.knowledge.repository.knowledges_vectors import \
    KnowledgesVectors
from ally.modules.knowledge.repository.storage import Storage
from ally.packages.embeddings.vectors import get_unique_files_from_vector_ids

logger = get_logger(__name__)


class KnowledgeVectorService:
	files: List[Any] = []

	def __init__(self, agent_id: str):
		self.repository = KnowledgesVectors()
		self.id = agent_id

	def create_agent_vector(self, vector_id, file_sha1):
		return self.repository.create_agent_vector(self.id, vector_id, file_sha1)

	def update_agent_with_file(self, file_sha1: str):
		# not  used
		vector_ids = self.repository.get_vector_ids_from_file_sha1(file_sha1)
		if vector_ids == None or len(vector_ids) == 0:
			logger.info(f"No vector ids found for file {file_sha1}")
			return

		for vector_id in vector_ids:
			self.create_agent_vector(vector_id, file_sha1)

	def get_unique_agent_files(self):
		"""
		Retrieve unique agent data (i.e. uploaded files and crawled websites).
		"""

		vector_ids = self.repository.get_agent_vector_ids(self.id)  # type: ignore
		self.files = get_unique_files_from_vector_ids(vector_ids)

		return self.files

	def delete_file_from_agent(self, file_name: str):
			file_name_with_agent_id = f"{self.id}/{file_name}"
			storage = Storage()
			storage.remove_file(file_name_with_agent_id)
			return self.repository.delete_file_from_agent(self.id, file_name)

	def delete_file_url_from_agent(self, file_name: str):
			return self.repository.delete_file_from_agent(self.id, file_name)

	@property
	def agent_size(self):
		# TODO: change the calculation of the agent size, calculate the size stored for the embeddings + what's in the storage
		self.get_unique_agent_files()
		current_agent_size = sum(float(doc["size"]) for doc in self.files)

		return current_agent_size
