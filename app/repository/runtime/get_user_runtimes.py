from uuid import UUID

from app.models import get_supabase_db
from app.models.runtimes import RuntimeEntity


def get_user_runtimes(user_id: UUID) -> list[RuntimeEntity]:
    """
    List all public runtimes
    """
    supabase_db = get_supabase_db()
    return supabase_db.get_user_runtimes(user_id)