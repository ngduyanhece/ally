
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.auth_bearer import AuthBearer, get_current_user
from app.models import Prompt
from app.models.databases.supabase.prompts import (CreatePromptProperties,
                                                   PromptUpdatableProperties)
from app.models.prompt import MinimalPromptEntity
from app.models.user_identity import UserIdentity
from app.repository.prompt.create_prompt import create_prompt
from app.repository.prompt.get_prompt_by_id import get_prompt_by_id
from app.repository.prompt.get_public_prompts import get_public_prompts
from app.repository.prompt.get_user_prompts import get_user_prompts
from app.repository.prompt.update_prompt_by_id import update_prompt_by_id

router = APIRouter()

@router.get(
	"/prompts",
	status_code=status.HTTP_200_OK,
	dependencies=[Depends(AuthBearer())])
async def get_prompts(
	current_user: UserIdentity = Depends(get_current_user),
) -> list[MinimalPromptEntity]:
	"""
	Retrieve all prompt of the current user
	"""

	return get_user_prompts(current_user.id)

@router.get(
	"/prompts/public",
	status_code=status.HTTP_200_OK,
	dependencies=[Depends(AuthBearer())])
async def get_all_public_prompts() -> list[MinimalPromptEntity]:
	"""
	Retrieve all public prompt
	"""

	return get_public_prompts()

@router.post(
	"/prompts",
	status_code=status.HTTP_201_CREATED,
	dependencies=[Depends(AuthBearer())])
async def create_prompt_route(
	prompt: CreatePromptProperties,
	current_user: UserIdentity = Depends(get_current_user)
) -> Prompt:
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
	prompt = get_prompt_by_id(prompt_id)
	if prompt is None:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Prompt not found"
		)
	return prompt

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
	prompt = update_prompt_by_id(prompt_id, prompt)
	if prompt is None:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Prompt not found"
		)
	return prompt
