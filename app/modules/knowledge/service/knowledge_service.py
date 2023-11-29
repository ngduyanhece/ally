from uuid import UUID

from app.logger import get_logger
from app.models.settings import get_supabase_client
from app.modules.knowledge.entity.knowledge import (CreateKnowledgeProperties,
                                                    KnowledgeEntity)
from app.modules.knowledge.repository.knowledge import Knowledge

logger = get_logger(__name__)

class KnowledgeService:
	repository: Knowledge

	def __init__(self):
		supabase_client = get_supabase_client()
		self.repository = Knowledge(supabase_client)
	
	def add_knowledge(self, knowledge_to_add: CreateKnowledgeProperties):
		knowledge = self.repository.insert_knowledge(knowledge_to_add)
		logger.info(f"Knowledge { knowledge.id} added successfully")
		return knowledge

	def get_all_knowledge_in_brain(self, brain_id: UUID) -> list[KnowledgeEntity]:
		return self.repository.get_all_knowledge_in_brain(brain_id)