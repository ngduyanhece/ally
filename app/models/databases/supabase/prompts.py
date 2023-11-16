from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.models.databases.repository import Repository
from app.models.prompt import (MinimalPromptEntity, Prompt,
                               PromptInputTemplate, PromptOutputTemplate,
                               PromptStatusEnum)


class CreatePromptProperties(BaseModel):
	"""Properties that can be received on prompt creation"""

	title: str
	content: str
	input_template: list[PromptInputTemplate]
	output_template: list[PromptOutputTemplate]
	status: PromptStatusEnum = PromptStatusEnum.private


class PromptUpdatableProperties(BaseModel):
	"""Properties that can be received on prompt update"""

	title: Optional[str]
	content: Optional[str]
	input_template: Optional[list[PromptInputTemplate]]
	output_template: Optional[list[PromptOutputTemplate]]
	status: Optional[PromptStatusEnum]


class DeletePromptResponse(BaseModel):
	"""Response when deleting a prompt"""

	status: str = "delete"
	prompt_id: UUID


class Prompts(Repository):
	def __init__(self, supabase_client):
		self.db = supabase_client

	def create_prompt(
			self, prompt: CreatePromptProperties, user_id) -> Prompt:
		"""
		Create a prompt
		"""
		prompt_response = (
			self.db.from_("prompts")
			.insert(
				{
					"title": prompt.title,
					"content": prompt.content,
					"status": prompt.status,
					"user_id": str(user_id),
				}
			)
			.execute()
		)
		for template in prompt.input_template:
			self.db.from_("prompt_input_templates").insert(
				{
					"name": template.name,
					"description": template.description,
					"prompt_id": prompt_response.data[0]["id"],
				}
			).execute()
		for template in prompt.output_template:
			self.db.from_("prompt_output_templates").insert(
				{
					"name": template.name,
					"description": template.description,
					"prompt_id": prompt_response.data[0]["id"],
				}
			).execute()

		prompt_entity = Prompt(
			**prompt_response.data[0],
			input_template=prompt.input_template,
			output_template=prompt.output_template,
		)
		
		return prompt_entity

	def delete_prompt_by_id(self, prompt_id: UUID) -> DeletePromptResponse:
		"""
		Delete a prompt by id
		Args:
			prompt_id (UUID): The id of the prompt

		Returns:
		A dictionary containing the status of the delete and prompt_id of the deleted prompt
		"""
		response = (
			self.db.from_("prompts")
			.delete()
			.filter("id", "eq", prompt_id)
			.execute()
			.data
		)

		if response == []:
			raise HTTPException(404, "Prompt not found")

		return DeletePromptResponse(status="deleted", prompt_id=prompt_id)

	def get_prompt_by_id(self, prompt_id: UUID) -> Prompt | None:
		"""
		Get a prompt by its id and join prompts, input_prompt_template and output_prompt_template

		Args:
			prompt_id (UUID): The id of the prompt

		Returns:
			Prompt: The prompt
		"""
		prompt_response = (
			self.db.from_("prompts")
			.select("*")
			.filter("id", "eq", prompt_id)
			.execute()
		).data

		if prompt_response == []:
			return None

		input_template = (
			self.db.from_("prompt_input_templates")
			.select("*")
			.filter("prompt_id", "eq", prompt_id)
			.execute()
		).data

		output_template = (
			self.db.from_("prompt_output_templates")
			.select("*")
			.filter("prompt_id", "eq", prompt_id)
			.execute()
		).data

		return Prompt(
			**prompt_response[0],
			input_template=input_template,
			output_template=output_template,
		)

	def get_public_prompts(self) -> list[MinimalPromptEntity]:
		"""
		List all public prompts
		"""

		return (
			self.db.from_("prompts")
			.select("*")
			.filter("status", "eq", "public")
			.execute()
		).data

	def update_prompt_by_id(
		self, prompt_id: UUID, prompt: PromptUpdatableProperties
	) -> Prompt | None:
		"""Update prompt by id  with input_template and output_template
		Args:
			prompt_id (UUID): The id of the prompt
			prompt (PromptUpdatableProperties): The prompt properties to update
		Returns:
			Prompt: The updated prompt
		"""
		prompt_response = (
			self.db.from_("prompts")
			.update(
				{
					"title": prompt.title,
					"content": prompt.content,
					"status": prompt.status,
				}
			)
			.filter("id", "eq", prompt_id)
			.execute()
		).data

		if prompt_response == []:
			return None
		for template in prompt.input_template:
			self.db.from_("prompt_input_templates").update(
				{
					"name": template.name,
					"description": template.description
				}
			).filter("prompt_id", "eq", prompt_id).execute()

		for template in prompt.output_template:
			self.db.from_("prompt_output_templates").update(
				{
					"name": template.name,
					"description": template.description
				}
			).filter("prompt_id", "eq", prompt_id).execute()
		
		return Prompt(
			**prompt_response[0],
			input_template=prompt.input_template,
			output_template=prompt.output_template,
		)
	
	def get_user_prompts(self, user_id: UUID) -> list[MinimalPromptEntity]:
		"""
		List all public prompts if for user_id join prompts, 
		input_prompt_template and output_prompt_template
		"""
		# first select all prompts for user_id
		response = (
			self.db.from_("prompts")
			.select("*")
			.filter("user_id", "eq", str(user_id))
			.execute()
		).data

		return response
		