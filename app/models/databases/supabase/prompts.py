from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from pydantic import BaseModel

from app.models.databases.repository import Repository
from app.models.prompt import Prompt, PromptStatusEnum


class CreatePromptProperties(BaseModel):
    """Properties that can be received on prompt creation"""

    title: str
    content: str
    status: PromptStatusEnum = PromptStatusEnum.private


class PromptUpdatableProperties(BaseModel):
    """Properties that can be received on prompt update"""

    title: Optional[str]
    content: Optional[str]
    status: Optional[PromptStatusEnum]


class DeletePromptResponse(BaseModel):
    """Response when deleting a prompt"""

    status: str = "delete"
    prompt_id: UUID


class Prompts(Repository):
    def __init__(self, supabase_client):
        self.db = supabase_client

    def create_prompt(self, prompt: CreatePromptProperties, user_id) -> Prompt:
        """
        Create a prompt
        """
        response = (
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

        return Prompt(**response.data[0])

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
        Get a prompt by its id

        Args:
            prompt_id (UUID): The id of the prompt

        Returns:
            Prompt: The prompt
        """

        response = (
            self.db.from_("prompts").select("*").filter("id", "eq", prompt_id).execute()
        ).data

        if response == []:
            return None
        return Prompt(**response[0])

    def get_public_prompts(self) -> list[Prompt]:
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
    ) -> Prompt:
        """Update a prompt by id"""

        response = (
            self.db.from_("prompts")
            .update(prompt.model_dump(exclude_unset=True))
            .filter("id", "eq", prompt_id)
            .execute()
        ).data

        if response == []:
            raise HTTPException(404, "Prompt not found")

        return Prompt(**response[0])
    
    def get_user_prompts(self, user_id: UUID) -> list[Prompt]:
        """
        List all prompts for a user
        """

        return (
            self.db.from_("prompts")
            .select("*")
            .filter("user_id", "eq", str(user_id))
            .execute()
        ).data
