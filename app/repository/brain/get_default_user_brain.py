from uuid import UUID

from app.logger import get_logger
from app.models import get_supabase_db
from app.models.brain_entity import MinimalBrainEntity
from app.repository.brain import get_brain_by_id

logger = get_logger(__name__)


def get_user_default_brain(user_id: UUID) -> MinimalBrainEntity | None:
    supabase_db = get_supabase_db()
    brain_id = supabase_db.get_default_user_brain_id(user_id)

    logger.info(f"Default brain response: {brain_id}")

    if brain_id is None:
        return None

    logger.info(f"Default brain id: {brain_id}")

    return get_brain_by_id(brain_id)
