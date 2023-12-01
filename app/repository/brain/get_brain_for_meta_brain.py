from uuid import UUID

from app.models.brain_entity import InfosBrainEntity
from app.models.settings import get_supabase_db


def get_brain_for_meta_brain(meta_brain_id: UUID) -> list[InfosBrainEntity] | None:
    supabase_db = get_supabase_db()
    return supabase_db.get_brain_for_meta_brain(meta_brain_id)
