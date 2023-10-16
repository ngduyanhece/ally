from uuid import UUID

from app.models import get_supabase_db
from app.models.meta_brain_entity import MinimalMetaBrainEntity


def get_user_meta_brains(user_id: UUID) -> list[MinimalMetaBrainEntity]:
    supabase_db = get_supabase_db()
    results = supabase_db.get_user_meta_brains(user_id)  # type: ignore

    return results  # type: ignore
