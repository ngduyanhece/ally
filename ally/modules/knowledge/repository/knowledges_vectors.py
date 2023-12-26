from uuid import UUID

from logger import get_logger

from ally.core.settings import get_supabase_client
from ally.modules.knowledge.repository.knowledges_vectors_interface import \
    KnowledgesVectorsInterface

logger = get_logger(__name__)


class KnowledgesVectors(KnowledgesVectorsInterface):
	
	def __init__(self):
		supabase_client = get_supabase_client()
		self.db = supabase_client

	def create_agent_vector(
		self,
		agent_id: str,
		vector_id: UUID,
		file_sha1: str
	):
		response = (
			self.db.table("agents_vectors")
			.insert(
				{
					"agent_id": agent_id,
					"vector_id": str(vector_id),
					"file_sha1": file_sha1,
				}
			)
			.execute()
		)
		return response.data

	def get_vector_ids_from_file_sha1(self, file_sha1: str):
		# move to vectors class
		vectorsResponse = (
			self.db.table("vectors")
			.select("id")
			.filter("file_sha1", "eq", file_sha1)
			.execute()
		)
		return vectorsResponse.data

	def get_agent_vector_ids(self, agent_id: str):
		"""
		Retrieve unique agent data (i.e. uploaded files and crawled websites).
		"""

		response = (
			self.db.from_("agents_vectors")
			.select("vector_id")
			.filter("agent_id", "eq", agent_id)
			.execute()
		)

		vector_ids = [item["vector_id"] for item in response.data]

		if len(vector_ids) == 0:
			return []

		return vector_ids

	def delete_file_from_agent(self, agent_id: str, file_name: str):
		# First, get the vector_ids associated with the file_name
		file_vectors = (
				self.db.table("vectors")
				.select("id")
				.filter("metadata->>file_name", "eq", file_name)
				.execute()
		)

		file_vectors_ids = [item["id"] for item in file_vectors.data]

		# remove current file vectors from agent vectors
		self.db.table("agents_vectors").delete().filter(
				"vector_id", "in", f"({','.join(map(str, file_vectors_ids))})"
		).filter("agent_id", "eq", agent_id).execute()

		vectors_used_by_another_agent = (
			self.db.table("agents_vectors")
			.select("vector_id")
			.filter("vector_id", "in", f"({','.join(map(str, file_vectors_ids))})")
			.filter("agent_id", "neq", agent_id)
			.execute()
		)

		vectors_used_by_another_agent_ids = [
			item["vector_id"] for item in vectors_used_by_another_agent.data
		]

		vectors_no_longer_used_ids = [
			id for id in file_vectors_ids if id not in vectors_used_by_another_agent_ids
		]

		self.db.table("vectors").delete().filter(
			"id", "in", f"({','.join(map(str, vectors_no_longer_used_ids))})"
		).execute()

		return {"message": f"File {file_name} in agent {agent_id} has been deleted."}

	def delete_agent_vector(self, agent_id: str):
		results = (
			self.db.table("agents_vectors")
			.delete()
			.match({"agent_id": agent_id})
			.execute()
		)

		return results
