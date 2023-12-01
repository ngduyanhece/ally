from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.models.runtimes import RuntimeEntity


class FullBrainEntity(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    status: Optional[str]
    prompt_id: Optional[UUID]
    runtime: Optional[RuntimeEntity]
    teacher_runtime: Optional[RuntimeEntity]
    last_update: str
class BrainEntity(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    status: Optional[str]
    prompt_id: Optional[UUID]
    runtime_id: Optional[UUID]
    teacher_runtime_id: Optional[UUID]
    last_update: str

class InfosBrainEntity(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    temperature: Optional[float]
    model: Optional[str]
    max_tokens: Optional[int]
    openai_api_key: Optional[str]


class PublicBrain(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    number_of_subscribers: int = 0
    last_update: str
