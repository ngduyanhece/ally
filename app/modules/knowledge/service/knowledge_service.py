from app.logger import get_logger
from app.models.settings import get_supabase_client
from app.modules.knowledge.entity.knowledge import CreateKnowledgeProperties
from app.modules.knowledge.repository.knowledge import Knowledge

logger = get_logger(__name__)

class KnowledgeService:
	repository: Knowledge

	def __init__(self):
		supabase_client = get_supabase_client()
		self.repository = Knowledge(supabase_client)
	
	def upload_file_storage(self, file, file_identifier: str):
		return self.repository.upload_file_storage(file, file_identifier)
	
	def add_knowledge(self, knowledge_to_add: CreateKnowledgeProperties):
		knowledge =  self.repository.insert_knowledge(knowledge_to_add)
		logger.info(f"Knowledge { knowledge.id} added successfully")
		return knowledge
