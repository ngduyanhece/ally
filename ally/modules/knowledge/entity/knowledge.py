from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class KnowledgeStatus(str, Enum):
	Pending = "Pending"
	Error = "Error"
	Done = "Done"

class KnowledgeEntity(BaseModel):
	id: UUID
	agent_id: str
	file_name: Optional[str] = None
	url: Optional[str] = None
	extension: str = "txt"
	status: Optional[str]
	message: Optional[str]
