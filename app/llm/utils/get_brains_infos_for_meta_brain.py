from typing import Optional
from uuid import UUID

from pydantic.v1 import BaseModel

from app.llm.llm_brain import LLMBrain
from app.logger import get_logger
from app.repository.brain.get_brain_for_meta_brain import \
    get_brain_for_meta_brain

logger = get_logger(__name__)
class ArgsSchema(BaseModel):
    chat_input: str
    use_history: bool = True

def get_brain_infos_for_meta_brain(meta_brain_id: Optional[UUID],chat_id: str):
    info_brain_entities = get_brain_for_meta_brain(meta_brain_id)
    logger.info(f"info_brain_entities: {info_brain_entities}")
    return [
        {
            "name": info_brain_entity.name,
            "description": info_brain_entity.description,
            "args_schema": ArgsSchema,
            "tool": LLMBrain,
            "tool_config": {
                "model": info_brain_entity.model,
                "max_tokens": info_brain_entity.max_tokens,
                "temperature": info_brain_entity.temperature,
                "brain_id": str(info_brain_entity.id),
                "user_openai_api_key": info_brain_entity.openai_api_key,
                "chat_id": chat_id,
                "prompt_id": 'None'
            }
        }
        for info_brain_entity in info_brain_entities
    ]
            

                                   