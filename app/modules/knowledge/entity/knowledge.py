from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class KnowledgeStatus(str, Enum):
	Pending = "Pending"
	Error = "Error"
	Done = "Done"

class CreateKnowledgeProperties(BaseModel):
	brain_id: UUID
	file_name: Optional[str] = None
	url: Optional[str] = None
	extension: str = "txt"
	status: KnowledgeStatus = KnowledgeStatus.Pending
	message: Optional[str] = None

	def dict(self, *args, **kwargs):
		knowledge_dict = super().model_dump(*args, **kwargs)
		knowledge_dict["brain_id"] = str(knowledge_dict.get("brain_id"))
		return knowledge_dict

class DeleteKnowledgeResponse(BaseModel):
	status: str = "delete"
	knowledge_id: UUID

class KnowledgeEntity(BaseModel):
	id: UUID
	brain_id: UUID
	file_name: Optional[str] = None
	url: Optional[str] = None
	extension: str = "txt"
	status: Optional[str]
	message: Optional[str]
