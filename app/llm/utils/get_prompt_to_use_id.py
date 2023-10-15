from typing import Optional
from uuid import UUID

from app.logger import get_logger
from app.repository.brain.get_brain_prompt_id import get_brain_prompt_id

logger = get_logger(__name__)

def get_prompt_to_use_id(
    brain_id: Optional[UUID], prompt_id: str
) -> Optional[UUID]:
    if prompt_id != 'None':
        return UUID(prompt_id)
    else:
        return get_brain_prompt_id(brain_id)
