from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from ally.modules.agent.dto.inputs import ModelTye


class RoleEnum(str, Enum):
	Viewer = "Viewer"
	Editor = "Editor"
	Owner = "Owner"


class AgentEntity(BaseModel):
	id: str
	name: str
	instructions: str
	model: Optional[ModelTye]
      

class AgentUser(BaseModel):
	id: str
	user_id: UUID
	rights: RoleEnum


class UserAgentEntity(BaseModel):
	id: str
	name: str
	instructions: str
	model: Optional[ModelTye]
	rights: RoleEnum