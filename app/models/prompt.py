from enum import Enum
from typing import List
from uuid import UUID

from pydantic import BaseModel


class PromptStatusEnum(str, Enum):
	private = "private"
	public = "public"

class PromptInputTemplate(BaseModel):
	name: str = "name"
	description: str = "description"

class PromptOutputTemplate(BaseModel):
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
	input_template: List[PromptInputTemplate]
	output_template: List[PromptOutputTemplate]
	status: PromptStatusEnum = PromptStatusEnum.private
