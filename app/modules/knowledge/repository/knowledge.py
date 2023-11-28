

from uuid import UUID

from fastapi import HTTPException

from app.modules.knowledge.entity import knowledge
from app.modules.knowledge.entity.knowledge import (CreateKnowledgeProperties,
                                                    DeleteKnowledgeResponse,
                                                    Knowledge)
from app.modules.knowledge.repository.knowledge_interface import \
    KnowledgeInterface


class Knowledge(KnowledgeInterface):
	def __init__(self, supabase_client):
		self.db = supabase_client
	
	def upload_file_storage(self, file, file_identifier: str):
		try:
			response = self.db.storage.from_("ally").upload(file_identifier, file)
			return response
		except Exception as e:
			raise e
	def insert_knowledge(self, knowledge: CreateKnowledgeProperties) -> knowledge:
		"""
		Add a knowledge
		"""
		response = (
			self.db.from_("knowledge").insert(knowledge.dict()).execute()).data
		return Knowledge(**response[0])

	def remove_knowledge_by_id(
		# todo: update remove brain endpoints to first delete the knowledge
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
			# change to response[0].brain_id and knowledge_id[0].brain_id
			status="deleted",
			knowledge_id=knowledge_id,
		)

	def get_knowledge_by_id(self, knowledge_id: UUID) -> Knowledge:
		"""
		Get a knowledge by its id
		Args:
				brain_id (UUID): The id of the brain
		"""
		knowledge = (
			self.db.from_("knowledge")
			.select("*")
			.filter("id", "eq", str(knowledge_id))
			.execute()
		).data

		return Knowledge(**knowledge[0])

	def get_all_knowledge_in_brain(self, brain_id: UUID) -> list[Knowledge]:
			"""
			Get all the knowledge in a brain
			Args:
					brain_id (UUID): The id of the brain
			"""
			all_knowledge = (
					self.db.from_("knowledge")
					.select("*")
					.filter("brain_id", "eq", str(brain_id))
					.execute()
			).data

			return [Knowledge(**knowledge) for knowledge in all_knowledge]

	def remove_brain_all_knowledge(self, brain_id: UUID) -> None:
		"""
		Remove all knowledge in a brain
		Args:
				brain_id (UUID): The id of the brain
		"""
		all_knowledge = self.get_all_knowledge_in_brain(brain_id)
		knowledge_to_delete_list = []

		for knowledge_item in all_knowledge:
			if knowledge_item.file_name:
					knowledge_to_delete_list.append(f"{brain_id}/{knowledge_item.file_name}")

		if knowledge_to_delete_list:
				self.db.storage.from_("ally").remove(knowledge_to_delete_list)

		self.db.from_("knowledge").delete().filter(
				"brain_id", "eq", str(brain_id)
		).execute()
