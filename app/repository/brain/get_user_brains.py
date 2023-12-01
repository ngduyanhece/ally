from uuid import UUID

from app.models import get_supabase_db
from app.models.brain_entity import FullBrainEntity


def get_user_brains(user_id: UUID) -> list[FullBrainEntity]:
    supabase_db = get_supabase_db()
    results = supabase_db.get_user_brains(user_id)  # type: ignore

    return results  # type: ignore
