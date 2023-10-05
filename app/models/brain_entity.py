from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.routes.authorizations.types import RoleEnum


class BrainEntity(BaseModel):
    brain_id: UUID
    name: str
    description: Optional[str]
    temperature: Optional[float]
    model: Optional[str]
    max_tokens: Optional[int]
    openai_api_key: Optional[str]
    status: Optional[str]
    prompt_id: Optional[UUID]
    last_update: str

    @property
    def id(self) -> UUID:
        return self.brain_id

    def dict(self, **kwargs):
        data = super().model_dump(
            **kwargs,
        )
        data["id"] = self.id
        return data
    

class MinimalBrainEntity(BaseModel):
    id: UUID
    name: str
    rights: RoleEnum
    status: str


class PublicBrain(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    number_of_subscribers: int = 0
    last_update: str
