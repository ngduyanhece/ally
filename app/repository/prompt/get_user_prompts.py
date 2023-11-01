from uuid import UUID

from app.models import Prompt, get_supabase_db


def get_user_prompts(user_id: UUID) -> list[Prompt]:
    """
    List all public prompts
    """
    supabase_db = get_supabase_db()
    return supabase_db.get_user_prompts(user_id)