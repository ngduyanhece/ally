from uuid import UUID

from app.models.databases.supabase.meta_brains import \
    MetaBrainUpdatableProperties
from app.models.meta_brain_entity import MetaBrainEntity
from app.models.settings import get_supabase_db
from app.repository.meta_brain.update_meta_brain_last_update_time import \
    update_meta_brain_last_update_time


def update_meta_brain_by_id(meta_brain_id: UUID, meta_brain: MetaBrainUpdatableProperties) -> MetaBrainEntity:
    """Update a prompt by id"""
    supabase_db = get_supabase_db()

    meta_brain_update_answer = supabase_db.update_meta_brain_by_id(meta_brain_id, meta_brain)
    if meta_brain_update_answer is None:
        raise Exception("Brain not found")

    update_meta_brain_last_update_time(meta_brain_id)
    return meta_brain_update_answer
