from uuid import UUID

from app.models import get_supabase_db
from app.models.prompt import MinimalPromptEntity


def get_user_prompts(user_id: UUID) -> list[MinimalPromptEntity]:
    """
    List all public prompts
    """
    supabase_db = get_supabase_db()
    return supabase_db.get_user_prompts(user_id)