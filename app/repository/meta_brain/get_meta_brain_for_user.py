from uuid import UUID

from app.models.meta_brain_entity import MinimalMetaBrainEntity
from app.models.settings import get_supabase_db


def get_meta_brain_for_user(user_id: UUID, meta_brain_id: UUID) -> MinimalMetaBrainEntity | None:
    supabase_db = get_supabase_db()
    return supabase_db.get_meta_brain_for_user(user_id, meta_brain_id)
