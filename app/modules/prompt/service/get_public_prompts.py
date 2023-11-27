from app.models import get_supabase_db
from app.models.prompt import MinimalPromptEntity


def get_public_prompts() -> list[MinimalPromptEntity]:
    """
    List all public prompts
    """
    supabase_db = get_supabase_db()
    return supabase_db.get_public_prompts()
