from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.auth.auth_bearer import AuthBearer, get_current_user
from app.models import Prompt
from app.models.databases.supabase.prompts import (CreatePromptProperties,
                                                   PromptUpdatableProperties)
from app.models.user_identity import UserIdentity
from app.repository.prompt.create_prompt import create_prompt
from app.repository.prompt.get_prompt_by_id import get_prompt_by_id
from app.repository.prompt.get_public_prompts import get_public_prompts
from app.repository.prompt.get_user_prompts import get_user_prompts
from app.repository.prompt.update_prompt_by_id import update_prompt_by_id

router = APIRouter()

@router.get("/prompts",
            status_code=status.HTTP_200_OK,
            dependencies=[Depends(AuthBearer())])
async def get_prompts(
    current_user: UserIdentity = Depends(get_current_user),
) -> list[Prompt]:
    """
    Retrieve all prompt of the current user
    """

    return get_user_prompts(current_user.id)

@router.get("/prompts/public",
            status_code=status.HTTP_200_OK,
            dependencies=[Depends(AuthBearer())])
async def get_all_public_prompts() -> list[Prompt]:
    """
    Retrieve all public prompt
    """

    return get_public_prompts()

@router.post("/prompts",
             status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(AuthBearer())])
async def create_prompt_route(
    prompt: CreatePromptProperties,
    current_user: UserIdentity = Depends(get_current_user)
) -> Prompt | None:
    """
    Create a prompt for the current user
    """

    return create_prompt(prompt, current_user.id)

@router.get(
    "/prompts/{prompt_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(AuthBearer())]
)
async def get_prompt(prompt_id: UUID) -> Prompt | None:
    """
    Retrieve a prompt by its id
    """

    return get_prompt_by_id(prompt_id)


@router.put(
    "/prompts/{prompt_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(AuthBearer())]
)
async def update_prompt(
    prompt_id: UUID, prompt: PromptUpdatableProperties
) -> Prompt | None:
    """
    Update a prompt by its id
    """

    return update_prompt_by_id(prompt_id, prompt)
