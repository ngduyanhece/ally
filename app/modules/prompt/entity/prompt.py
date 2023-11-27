from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class PromptStatusEnum(str, Enum):
	private = "private"
	public = "public"

class CreatePromptProperties(BaseModel):
	"""Properties use to create a prompt"""
	title: str
	content: str
	status: PromptStatusEnum = PromptStatusEnum.private

class UpdatePromptProperties(BaseModel):
	"""Properties that can be received on prompt update"""
	title: Optional[str]
	content: Optional[str]
	status: Optional[PromptStatusEnum]

class CreatePromptInputTemplateProperties(BaseModel):
	name: str = "name"
	description: str = "description"

class UpdatePromptInputTemplateProperties(BaseModel):
	id: UUID
	name: str = "name"
	description: str = "description"

class PromptInputTemplateEntity(BaseModel):
	id: UUID
	name: str = "name"
	description: str = "description"

class CreatePromptOutputTemplateProperties(BaseModel):
	name: str = "name"
	description: str = "description"

class UpdatePromptOutputTemplateProperties(BaseModel):
	id: UUID
	name: str = "name"
	description: str = "description"

class PromptOutputTemplateEntity(BaseModel):
	id: UUID
	name: str = "name"
	description: str = "description"

class MinimalPromptEntity(BaseModel):
	id: UUID
	title: str
	content: str
	status: PromptStatusEnum = PromptStatusEnum.private

class Prompt(BaseModel):
	id: UUID
	title: str
	content: str
	input_template: list[PromptInputTemplateEntity]
	output_template: list[PromptOutputTemplateEntity]
	status: PromptStatusEnum = PromptStatusEnum.private
