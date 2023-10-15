from typing import Optional
from uuid import UUID

from app.llm.utils.get_prompt_to_use_id import get_prompt_to_use_id
from app.logger import get_logger
from app.models.prompt import Prompt
from app.repository.prompt import get_prompt_by_id

logger = get_logger(__name__)


def get_prompt_to_use(
    brain_id: Optional[UUID], prompt_id: Optional[UUID]
) -> Optional[Prompt]:
    prompt_to_use_id = get_prompt_to_use_id(brain_id, prompt_id)
    if prompt_to_use_id is None:
        return None
    return get_prompt_by_id(prompt_to_use_id)
