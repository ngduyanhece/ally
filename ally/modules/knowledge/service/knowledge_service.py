from uuid import UUID

from ally.logger import get_logger
from ally.modules.knowledge.dto.inputs import CreateKnowledgeProperties
from ally.modules.knowledge.entity.knowledge import KnowledgeEntity
from ally.modules.knowledge.repository.knowledges import Knowledges

logger = get_logger(__name__)

class KnowledgeService:

	def __init__(self):
		self.repository = Knowledges()
	
	def add_knowledge(self, knowledge_to_add: CreateKnowledgeProperties):
		knowledge = self.repository.insert_knowledge(knowledge_to_add)
		logger.info(f"Knowledge { knowledge.id} added successfully")
		return knowledge

	def get_all_knowledge_in_agent(self, agent_id: str) -> list[KnowledgeEntity]:
		return self.repository.get_all_knowledge_in_agent(agent_id)
	
	def get_knowledge(self, knowledge_id: UUID) -> KnowledgeEntity:
		knowledge = self.repository.get_knowledge_by_id(knowledge_id)
		return knowledge
	
	def remove_agent_all_knowledge(self, agent_id: str) -> None:
		self.repository.remove_agent_all_knowledge(agent_id)

		logger.info(
				f"All knowledge in agent {agent_id} removed successfully from table"
		)

	def remove_knowledge(self, knowledge_id: UUID):
		message = self.repository.remove_knowledge_by_id(knowledge_id)

		logger.info(f"Knowledge { knowledge_id} removed successfully from table")

		return message
	
	def update_knowledge_property_by_id(
			self, knowledge_id: UUID, property: dict) -> KnowledgeEntity:
		return self.repository.update_knowledge_property_by_id(
			knowledge_id, property)
	
