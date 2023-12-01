from uuid import UUID

from app.models.runtimes import RuntimeEntity
from app.models.settings import get_supabase_db


def get_runtime_by_id(runtime_id: UUID) -> RuntimeEntity | None:
    """
    Get a prompt by its id

    Args:
        prompt_id (UUID): The id of the prompt

    Returns:
        Prompt: The prompt
    """
    supabase_db = get_supabase_db()
    return supabase_db.get_runtime_by_id(runtime_id)
