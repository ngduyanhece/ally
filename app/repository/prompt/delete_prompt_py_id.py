from uuid import UUID

from app.models import get_supabase_db
from app.models.databases.supabase.prompts import DeletePromptResponse


def delete_prompt_by_id(prompt_id: UUID) -> DeletePromptResponse:
    """
    Delete a prompt by id
    Args:
        prompt_id (UUID): The id of the prompt

    Returns:
        Prompt: The prompt
    """
    supabase_db = get_supabase_db()
    return supabase_db.delete_prompt_by_id(prompt_id)
