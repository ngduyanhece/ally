from uuid import UUID

from app.modules.prompt.entity.prompt import (
    CreatePromptInputTemplateProperties, CreatePromptOutputTemplateProperties,
    CreatePromptProperties, MinimalPromptEntity, Prompt,
    PromptInputTemplateEntity, PromptOutputTemplateEntity,
    UpdatePromptInputTemplateProperties, UpdatePromptOutputTemplateProperties,
    UpdatePromptProperties)
from app.modules.prompt.repository.prompts_interface import PromptsInterface


class Prompts(PromptsInterface):
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
		# create input template and output template for a prompt
		# TODO: will let user create input template and output template
		# for now, we will create default input template and output template

		input_template = self.create_prompt_input_template_by_prompt_id(
			prompt_id=prompt_response.data[0]["id"],
			prompt_input_template=CreatePromptInputTemplateProperties(
				name="text_input",
				description="input from human",
			)
		)

		output_template = self.create_prompt_output_template_by_prompt_id(
			prompt_id=prompt_response.data[0]["id"],
			prompt_output_template=CreatePromptOutputTemplateProperties(
				name="output",
				description="this is the final output from the system",
			)
		)

		prompt_entity = Prompt(
			**prompt_response.data[0],
			input_template=[
				PromptInputTemplateEntity(**input_template.model_dump())],
			output_template=[
				PromptOutputTemplateEntity(**output_template.model_dump())],
		)
		
		return prompt_entity

	def delete_prompt_by_id(self, prompt_id: UUID):
		"""
		Delete a prompt by id
		Args:
			prompt_id (UUID): The id of the prompt

		Returns:
		A dictionary containing the status of the delete and prompt_id of the deleted prompt
		"""
		prompt_response = (
			self.db.from_("prompts")
			.delete()
			.filter("id", "eq", prompt_id)
			.execute()
			.data
		)
		if prompt_response == []:
			raise Exception(404, "Prompt not found")
		
		prompt_input_template_response = (
			self.db.from_("prompt_input_templates")
			.delete()
			.filter("prompt_id", "eq", prompt_id)
			.execute()
			.data
		)

		prompt_output_template_response = (
			self.db.from_("prompt_output_templates")
			.delete()
			.filter("prompt_id", "eq", prompt_id)
			.execute()
			.data
		)
	
		for input_template in prompt_input_template_response:
			self.delete_prompt_input_template_by_id(input_template["input_template_id"])
		
		for output_template in prompt_output_template_response:
			self.delete_prompt_output_template_by_id(output_template["output_template_id"])

		return prompt_response[0]

	def get_prompt_by_id(self, prompt_id: UUID) -> Prompt | None:
		"""
		Get a prompt by its id and join prompts, 
		input_prompt_template and output_prompt_template

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
		self, prompt_id: UUID, prompt: UpdatePromptProperties
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

		# get prompt input template and output template
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
			input_template=[
				PromptInputTemplateEntity(**template) for template in input_template],
			output_template=[
				PromptOutputTemplateEntity(**template) for template in output_template],
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
	
	def get_all_prompt_input_template_by_prompt_id(
		self, prompt_id: UUID
	) -> list[PromptInputTemplateEntity]:
		"""
		List all prompt input template for a prompt
		"""
		response = (
			self.db.from_("prompt_input_templates")
			.select("*")
			.filter("prompt_id", "eq", prompt_id)
			.execute()
		).data

		return response
	
	def get_prompt_input_template_by_id(
		self, prompt_input_template_id: UUID
	) -> PromptInputTemplateEntity | None:
		"""
		Get a prompt input template by id
		"""
		response = (
			self.db.from_("prompt_input_templates")
			.select("*")
			.filter("input_template_id", "eq", prompt_input_template_id)
			.execute()
		).data

		if response == []:
			return None

		return PromptInputTemplateEntity(
			**response[0],
		)
	
	def create_prompt_input_template_by_prompt_id(
		self,
		prompt_id: UUID,
		prompt_input_template: CreatePromptInputTemplateProperties
	) -> PromptInputTemplateEntity:
		"""
		Create a prompt input template
		"""
		prompt_response = (
			self.db.from_("prompt_input_templates")
			.insert(
				{
					"name": prompt_input_template.name,
					"description": prompt_input_template.description,
					"prompt_id": str(prompt_id),
				}
			)
			.execute()
		)
		return PromptInputTemplateEntity(
			**prompt_response.data[0],
		)
	
	def update_prompt_input_template_by_id(
		self,
		prompt_input_template_id: UUID,
		prompt_input_template: UpdatePromptInputTemplateProperties
	) -> PromptInputTemplateEntity | None:
		"""
		Update a prompt input template
		"""
		response = (
			self.db.from_("prompt_input_templates")
			.update(
				{
					"name": prompt_input_template.name,
					"description": prompt_input_template.description,
				}
			)
			.filter("input_template_id", "eq", prompt_input_template_id)
			.execute()
		).data

		if response == []:
			return None

		return PromptInputTemplateEntity(
			**response[0],
		)
	
	def delete_prompt_input_template_by_id(
		self, prompt_input_template_id: UUID
	) -> PromptInputTemplateEntity | None:
		"""
		Delete a prompt input template
		"""
		response = (
			self.db.from_("prompt_input_templates")
			.delete()
			.filter("input_template_id", "eq", prompt_input_template_id)
			.execute()
		).data

		if response == []:
			return None

		return PromptInputTemplateEntity(
			**response[0],
		)
	
	def get_all_prompt_output_template_by_prompt_id(
		self, prompt_id: UUID
	) -> list[PromptOutputTemplateEntity]:
		"""
		List all prompt output template for a prompt
		"""
		response = (
			self.db.from_("prompt_output_templates")
			.select("*")
			.filter("prompt_id", "eq", prompt_id)
			.execute()
		).data

		return response
	
	def get_prompt_output_template_by_id(
			self, prompt_output_template_id: UUID
	) -> PromptOutputTemplateEntity | None:
		"""
		Get a prompt output template by id
		"""
		response = (
			self.db.from_("prompt_output_templates")
			.select("*")
			.filter("output_template_id", "eq", prompt_output_template_id)
			.execute()
		).data

		if response == []:
			return None

		return PromptOutputTemplateEntity(
			**response[0],
		)
	
	def create_prompt_output_template_by_prompt_id(
		self,
		prompt_id: UUID,
		prompt_output_template: CreatePromptOutputTemplateProperties
	) -> PromptOutputTemplateEntity:
		"""
		Create a prompt output template
		"""
		prompt_response = (
			self.db.from_("prompt_output_templates")
			.insert(
				{
					"name": prompt_output_template.name,
					"description": prompt_output_template.description,
					"prompt_id": str(prompt_id),
				}
			)
			.execute()
		)
		return PromptOutputTemplateEntity(
			**prompt_response.data[0],
		)
	
	def update_prompt_output_template_by_id(
		self,
		prompt_output_template_id: UUID,
		prompt_output_template: UpdatePromptOutputTemplateProperties
	) -> PromptOutputTemplateEntity | None:
		"""
		Update a prompt output template
		"""
		response = (
			self.db.from_("prompt_output_templates")
			.update(
				{
					"name": prompt_output_template.name,
					"description": prompt_output_template.description,
				}
			)
			.filter("output_template_id", "eq", prompt_output_template_id)
			.execute()
		).data

		if response == []:
			return None

		return PromptOutputTemplateEntity(
			**response[0],
		)
	
	def delete_prompt_output_template_by_id(
		self, prompt_output_template_id: UUID
	) -> PromptOutputTemplateEntity | None:
		"""
		Delete a prompt output template
		"""
		response = (
			self.db.from_("prompt_output_templates")
			.delete()
			.filter("output_template_id", "eq", prompt_output_template_id)
			.execute()
		).data

		if response == []:
			return None

		return PromptOutputTemplateEntity(
			**response[0],
		)
			