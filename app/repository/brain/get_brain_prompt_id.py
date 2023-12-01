from uuid import UUID

from app.logger import get_logger
from app.repository.brain import get_brain_by_id

logger = get_logger(__name__)

def get_brain_prompt_id(brain_id: UUID) -> UUID | None:
    logger.info(f"brain_id: {brain_id}")
    brain = get_brain_by_id(brain_id)
    prompt_id = brain.prompt_id if brain else None

    return prompt_id
