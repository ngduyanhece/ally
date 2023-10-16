from uuid import UUID

from app.models.meta_brain_entity import MetaBrainEntity
from app.models.settings import get_supabase_db


def get_meta_brain_by_id(brain_id: UUID) -> MetaBrainEntity | None:
    supabase_db = get_supabase_db()

    return supabase_db.get_meta_brain_by_id(brain_id)
