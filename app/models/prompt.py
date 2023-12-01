from enum import Enum
from typing import List
from uuid import UUID

from pydantic import BaseModel


class PromptStatusEnum(str, Enum):
	private = "private"
	public = "public"

class PromptInputTemplate(BaseModel):
	input_template_id: UUID
	name: str = "name"
	description: str = "description"

	@property
	def id(self) -> UUID:
		return self.input_template_id

	def dict(self, **kwargs):
		data = super().model_dump(
				**kwargs,
		)
		data["id"] = self.id
		return data

class PromptOutputTemplate(BaseModel):
	output_template_id: UUID
	name: str = "name"
	description: str = "description"

	@property
	def id(self) -> UUID:
		return self.output_template_id

	def dict(self, **kwargs):
		data = super().model_dump(
			**kwargs,
		)
		data["id"] = self.id
		return data

class PromptInputTemplateEntity(BaseModel):
	name: str = "name"
	description: str = "description"

	def dict(self, **kwargs):
		data = super().model_dump(
			**kwargs,
		)
		return data

class PromptOutputTemplateEntity(BaseModel):
	name: str = "name"
	description: str = "description"

	def dict(self, **kwargs):
		data = super().model_dump(
			**kwargs,
		)
		return data

class MinimalPromptEntity(BaseModel):
	id: UUID
	title: str
	content: str
	status: PromptStatusEnum = PromptStatusEnum.private

class Prompt(BaseModel):
	id: UUID
	title: str
	content: str
	input_template: List[PromptInputTemplateEntity]
	output_template: List[PromptOutputTemplateEntity]
	status: PromptStatusEnum = PromptStatusEnum.private
