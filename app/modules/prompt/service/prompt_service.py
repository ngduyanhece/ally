from uuid import UUID

from app.models.settings import get_supabase_client
from app.modules.prompt.entity.prompt import (CreatePromptProperties,
                                              MinimalPromptEntity, Prompt,
                                              UpdatePromptProperties)
from app.modules.prompt.repository.prompts import Prompts


class PromptService:
	repository: Prompts

	def __init__(self):
		supabase_client = get_supabase_client()
		self.repository = Prompts(supabase_client)

	def create_prompt(
		self, prompt: CreatePromptProperties, user_id: UUID) -> Prompt:
		return self.repository.create_prompt(prompt, user_id)
	
	def get_user_prompts(self, user_id: UUID) -> list[MinimalPromptEntity]:
		"""
		List all public prompts
		"""
		return self.repository.get_user_prompts(user_id)
	
	def get_prompt_by_id(self, prompt_id: UUID) -> Prompt | None:
		"""
		Get a prompt by id
		"""
		return self.repository.get_prompt_by_id(prompt_id)

	def update_prompt_by_id(
			self, prompt_id: UUID, prompt: UpdatePromptProperties) -> Prompt:
		"""Update a prompt by id"""
		return self.repository.update_prompt_by_id(prompt_id, prompt)
	
	def delete_prompt_by_id(self, prompt_id: UUID) -> Prompt | None:
		"""
		Delete a prompt by id
		"""
		return self.repository.delete_prompt_by_id(prompt_id)