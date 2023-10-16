from uuid import UUID

from app.logger import get_logger
from app.models.meta_brain_entity import MetaBrainEntity
from app.models.settings import get_supabase_db
from app.repository.meta_brain.get_meta_brain_by_id import get_meta_brain_by_id

logger = get_logger(__name__)


def get_user_default_meta_brain(user_id: UUID) -> MetaBrainEntity | None:
    supabase_db = get_supabase_db()
    meta_brain_id = supabase_db.get_default_user_meta_brain_id(user_id)

    logger.info(f"Default meta brain response: {meta_brain_id}")

    if meta_brain_id is None:
        return None

    logger.info(f"Default meta brain id: {meta_brain_id}")

    return get_meta_brain_by_id(meta_brain_id)
