from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.prompt.entity.prompt import (CreatePromptProperties,
                                              MinimalPromptEntity, Prompt,
                                              UpdatePromptProperties)


class PromptsInterface(ABC):
	@abstractmethod
	def create_prompt(
		self, prompt: CreatePromptProperties, user_id: UUID) -> Prompt:
		"""
		Create a prompt
		"""
		pass
	
	def delete_prompt_by_id(self, prompt_id: UUID):
		"""
		Delete a prompt by id
		"""
		pass

	def get_prompt_by_id(self, prompt_id: UUID) -> Prompt | None:
		"""
		Get a prompt by id
		"""
		pass

	def update_prompt_by_id(
		self, prompt_id: UUID, prompt: UpdatePromptProperties
	) -> Prompt | None:
		"""
		Update a prompt by id
		"""
		pass

	def get_user_prompts(self, user_id: UUID) -> list[MinimalPromptEntity]:
		"""
		List all public prompts
		"""
		pass