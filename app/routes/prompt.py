from uuid import UUID

from fastapi import APIRouter, Depends

from app.auth.auth_bearer import AuthBearer
from app.models import Prompt
from app.models.databases.supabase.prompts import (CreatePromptProperties,
                                                   PromptUpdatableProperties)
from app.repository.prompt import get_prompt_by_id, get_public_prompts
from app.repository.prompt.create_prompt import create_prompt
from app.repository.prompt.update_prompt_by_id import update_prompt_by_id

router = APIRouter()

@router.get("/prompts", dependencies=[Depends(AuthBearer())])
async def get_prompts() -> list[Prompt]:
    """
    Retrieve all public prompt
    """

    return get_public_prompts()

@router.post("/prompts", dependencies=[Depends(AuthBearer())])
async def create_prompt_route(prompt: CreatePromptProperties) -> Prompt | None:
    """
    Create a prompt by its id
    """

    return create_prompt(prompt)

@router.get(
    "/prompts/{prompt_id}", dependencies=[Depends(AuthBearer())]
)
async def get_prompt(prompt_id: UUID) -> Prompt | None:
    """
    Retrieve a prompt by its id
    """

    return get_prompt_by_id(prompt_id)


@router.put(
    "/prompts/{prompt_id}", dependencies=[Depends(AuthBearer())]
)
async def update_prompt(
    prompt_id: UUID, prompt: PromptUpdatableProperties
) -> Prompt | None:
    """
    Update a prompt by its id
    """

    return update_prompt_by_id(prompt_id, prompt)
