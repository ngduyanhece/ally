from app.models import Prompt, get_supabase_db
from app.models.databases.supabase.prompts import CreatePromptProperties


def create_prompt(prompt: CreatePromptProperties) -> Prompt:
    supabase_db = get_supabase_db()

    return supabase_db.create_prompt(prompt)
