from uuid import UUID

from fastapi import HTTPException

from ally.core.settings import get_supabase_client
from ally.modules.knowledge.dto.inputs import CreateKnowledgeProperties
from ally.modules.knowledge.dto.outputs import DeleteKnowledgeResponse
from ally.modules.knowledge.entity.knowledge import KnowledgeEntity
from ally.modules.knowledge.repository.knowledges_interface import \
    KnowledgeInterface


class Knowledges(KnowledgeInterface):
	def __init__(self):
		supabase_client = get_supabase_client()
		self.db = supabase_client
		
	def insert_knowledge(
		self, knowledge: CreateKnowledgeProperties) -> KnowledgeEntity:
		"""
		Add a knowledge
		"""
		response = (
			self.db.from_("knowledge").insert(knowledge.dict()).execute()).data
		return KnowledgeEntity(**response[0])

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
		response = (
			self.db.from_("knowledge")
			.delete()
			.filter("id", "eq", knowledge_id)
			.execute()
			.data
		)

		if response == []:
			raise HTTPException(404, "Knowledge not found")

		return DeleteKnowledgeResponse(
			status="deleted",
			knowledge_id=knowledge_id,
		)

	def get_knowledge_by_id(self, knowledge_id: UUID) -> KnowledgeEntity:
		"""
		Get a knowledge by its id
		Args:
			knowledge_id (UUID): The id of the knowledge
		"""
		knowledge = (
			self.db.from_("knowledge")
			.select("*")
			.filter("id", "eq", str(knowledge_id))
			.execute()
		).data

		return KnowledgeEntity(**knowledge[0])
	
	def update_knowledge_property_by_id(
			self, knowledge_id: UUID, property: dict) -> KnowledgeEntity:
		"""
		Update a knowledge property by its id
		Args:
			knowledge_id (UUID): The id of the knowledge
			value: The value to update
		"""
		response = (
			self.db.from_("knowledge")
			.update(property)
			.filter("id", "eq", str(knowledge_id))
			.execute()
		).data

		if response == []:
			raise HTTPException(404, "Knowledge not found")

		return KnowledgeEntity(**response[0])

	def get_all_knowledge_in_agent(self, agent_id: str) -> list[KnowledgeEntity]:
		"""
		Get all the knowledge in an agent
		Args:
			agent_id (str): The id of the agent
		"""
		all_knowledge = (
			self.db.from_("knowledge")
			.select("*")
			.filter("agent_id", "eq", str(agent_id))
			.execute()
		).data

		return [KnowledgeEntity(**knowledge) for knowledge in all_knowledge]

	def remove_agent_all_knowledge(self, agent_id: str) -> None:
		"""
		Remove all knowledge in an agent
		Args:
			agent_id (UUID): The id of the agent
		"""
		all_knowledge = self.get_all_knowledge_in_agent(agent_id)
		knowledge_to_delete_list = []

		for knowledge_item in all_knowledge:
			if knowledge_item.file_name:
				knowledge_to_delete_list.append(f"{agent_id}/{knowledge_item.file_name}")

		if knowledge_to_delete_list:
			self.db.storage.from_("ally").remove(knowledge_to_delete_list)

		self.db.from_("knowledge").delete().filter(
			"agent_id", "eq", str(agent_id)
		).execute()
