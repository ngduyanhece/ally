from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.middlewares.auth.auth_bearer import AuthBearer, get_current_user
from app.modules.prompt.entity.prompt import (CreatePromptProperties,
                                              MinimalPromptEntity, Prompt,
                                              UpdatePromptProperties)
from app.modules.prompt.service.prompt_service import PromptService
from app.modules.user.entity.user_identity import UserIdentity

prompt_router = APIRouter()

promptService = PromptService()

@prompt_router.post(
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
	try:
		return promptService.create_prompt(prompt, current_user.id)
	except Exception as e:
		raise HTTPException(status_code=400, detail="cannot create a prompt")
	
@prompt_router.get(
	"/prompts",
	status_code=status.HTTP_200_OK,
	dependencies=[Depends(AuthBearer())])
async def get_prompts(
	current_user: UserIdentity = Depends(get_current_user),
) -> list[MinimalPromptEntity]:
	"""
	Retrieve all prompt of the current user
	"""
	
	return promptService.get_user_prompts(current_user.id)

@prompt_router.get(
	"/prompts/{prompt_id}",
	status_code=status.HTTP_200_OK,
	dependencies=[Depends(AuthBearer())]
)
async def get_prompt(prompt_id: UUID) -> Prompt | None:
	"""
	Retrieve a prompt by its id
	"""
	prompt = promptService.get_prompt_by_id(prompt_id)
	if prompt is None:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Prompt not found"
		)
	return prompt

@prompt_router.put(
	"/prompts/{prompt_id}",
	status_code=status.HTTP_200_OK,
	dependencies=[Depends(AuthBearer())]
)
async def update_prompt(
	prompt_id: UUID, prompt: UpdatePromptProperties
) -> Prompt | None:
	"""
	Update a prompt by its id
	"""
	prompt = promptService.update_prompt_by_id(prompt_id, prompt)
	if prompt is None:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Prompt not found"
		)
	return prompt

@prompt_router.delete(
	"/prompts/{prompt_id}",
	status_code=status.HTTP_200_OK,
	dependencies=[Depends(AuthBearer())]
)
async def delete_prompt(prompt_id: UUID):
	"""
	Delete a prompt by its id
	"""
	try:
		prompt = promptService.delete_prompt_by_id(prompt_id)
		return prompt
	except Exception as e:
		raise HTTPException(status_code=400, detail=str(e))
