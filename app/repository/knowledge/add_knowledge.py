from app.logger import get_logger
from app.models.databases.supabase.knowledge import CreateKnowledgeProperties
from app.models.settings import get_supabase_db

logger = get_logger(__name__)


def add_knowledge(knowledge_to_add: CreateKnowledgeProperties):
    supabase_db = get_supabase_db()

    knowledge = supabase_db.insert_knowledge(knowledge_to_add)

    logger.info(f"Knowledge { knowledge.id} added successfully")
    return knowledge
