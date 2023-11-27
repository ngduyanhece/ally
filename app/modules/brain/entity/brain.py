

from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class RoleEnum(str, Enum):
	Viewer = "Viewer"
	Editor = "Editor"
	Owner = "Owner"

class RuntimeType(str, Enum):
	OpenAi = "OpenAi"
	HuggingFace = "HuggingFace"
			 
class RuntimeEntity(BaseModel):
	id: UUID
	type: RuntimeType = RuntimeType.OpenAi
	name: str = "Default Runtime"
	model: str = "gpt-3.5"
	max_tokens: int = 256
	temperature: float = 0.9
	openai_api_key: str = ""

class CreateRuntimeProperties(BaseModel):
	"""Properties that can be received on runtime creation"""
	type: RuntimeType = RuntimeType.OpenAi
	name: str = "Default Runtime"
	model: str = "gpt-3.5-turbo"
	max_tokens: int = 256
	temperature: float = 0.9
	openai_api_key: Optional[str] = "place your openai api key here"


class CreateBrainProperties(BaseModel):
	name: Optional[str] = "Default brain"
	description: Optional[str] = "This is a description"
	status: Optional[str] = "private"
	prompt_id: Optional[UUID] = None


class CreateFullBrainProperties(BaseModel):
	name: Optional[str] = "Default brain"
	description: Optional[str] = "This is a description"
	status: Optional[str] = "private"
	prompt_id: Optional[UUID] = None
	runtime_id: Optional[UUID] = None
	teacher_runtime_id: Optional[UUID] = None


class FullBrainEntity(BaseModel):
	id: UUID
	name: str
	description: Optional[str]
	status: Optional[str]
	prompt_id: Optional[UUID]
	runtime: Optional[RuntimeEntity]
	teacher_runtime: Optional[RuntimeEntity]
	last_update: str

class FullBrainEntityWithRights(FullBrainEntity):
	rights: Optional[RoleEnum]

class MinimalBrainEntity(BaseModel):
	id: UUID
	name: str
	rights: Optional[RoleEnum]
	status: Optional[str]

class BrainEntity(BaseModel):
	id: UUID
	name: str
	description: Optional[str]
	status: Optional[str]
	prompt_id: Optional[UUID]
	runtime_id: Optional[UUID]
	teacher_runtime_id: Optional[UUID]
	last_update: str

class UpdateBrainProperties(BaseModel):
	name: Optional[str]
	description: Optional[str]
	status: Optional[str]
	prompt_id: Optional[UUID]