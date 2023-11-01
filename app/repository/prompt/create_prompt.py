from uuid import UUID

from app.models import Prompt, get_supabase_db
from app.models.databases.supabase.prompts import CreatePromptProperties


def create_prompt(prompt: CreatePromptProperties, user_id: UUID) -> Prompt:
    supabase_db = get_supabase_db()

    return supabase_db.create_prompt(prompt, user_id)
