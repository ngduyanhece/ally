from enum import Enum
from typing import Optional
from uuid import UUID

from modules.agent.dto.inputs import ModelTye
from pydantic import BaseModel


class RoleEnum(str, Enum):
	Viewer = "Viewer"
	Editor = "Editor"
	Owner = "Owner"


class AgentEntity(BaseModel):
	id: str
	name: str
	description: Optional[str]
	icon: Optional[str]
	instructions: str
	model: Optional[ModelTye]
      

class AgentUser(BaseModel):
	id: str
	user_id: UUID
	rights: RoleEnum


class UserAgentEntity(BaseModel):
	id: str
	name: str
	description: Optional[str]
	icon: Optional[str]
	instructions: str
	model: Optional[ModelTye]
	rights: RoleEnum

class ToolEntity(BaseModel):
	id: UUID
	name: str