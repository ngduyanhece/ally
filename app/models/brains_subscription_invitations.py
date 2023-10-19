from uuid import UUID

from pydantic import BaseModel

from app.logger import get_logger

logger = get_logger(__name__)


class BrainSubscription(BaseModel):
    brain_id: UUID
    email: str
    rights: str = "Viewer"

    class Config:
        arbitrary_types_allowed = True
