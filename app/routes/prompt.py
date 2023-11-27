
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth.auth_bearer import AuthBearer
from app.models.databases.supabase.prompts import (
    PromptInputTemplateProperties, PromptOutputTemplateProperties)
from app.models.prompt import (MinimalPromptEntity, PromptInputTemplate,
                               PromptOutputTemplate)
from app.repository.prompt.create_prompt_input_template_by_prompt_id import \
    create_prompt_input_template_by_prompt_id
from app.repository.prompt.create_prompt_output_template_by_prompt_id import \
    create_prompt_output_template_by_prompt_id
from app.repository.prompt.delete_prompt_input_template_by_id import \
    delete_prompt_input_template_by_id
from app.repository.prompt.delete_prompt_output_template_by_id import \
    delete_prompt_output_template_by_id
from app.repository.prompt.get_all_prompt_input_template_by_prompt_id import \
    get_all_prompt_input_template_by_prompt_id
from app.repository.prompt.get_all_prompt_output_template_by_prompt_id import \
    get_all_prompt_output_template_by_prompt_id
from app.repository.prompt.get_prompt_input_template_by_id import \
    get_prompt_input_template_by_id
from app.repository.prompt.get_prompt_output_template_by_id import \
    get_prompt_output_template_by_id
from app.repository.prompt.get_public_prompts import get_public_prompts
from app.repository.prompt.update_prompt_input_template_by_id import \
    update_prompt_input_template_by_id
from app.repository.prompt.update_prompt_output_template_by_id import \
    update_prompt_output_template_by_id

router = APIRouter()



@router.get(
	"/prompts/public",
	status_code=status.HTTP_200_OK,
	dependencies=[Depends(AuthBearer())])
async def get_all_public_prompts() -> list[MinimalPromptEntity]:
	"""
	Retrieve all public prompt
	"""

	return get_public_prompts()

@router.get(
	"/prompt_input_templates",
	status_code=status.HTTP_200_OK,
	dependencies=[Depends(AuthBearer())])
async def get_all_prompt_input_template_by_prompt_id_route(
	prompt_id: UUID = Query(..., description="The ID of the prompt")
) -> List[PromptInputTemplate]:
	"""
	Get a prompt input template by prompt id
	"""
	return get_all_prompt_input_template_by_prompt_id(prompt_id)

@router.get(
	"/prompt_input_templates/{prompt_input_template_id}",
	status_code=status.HTTP_200_OK,
	dependencies=[Depends(AuthBearer())])
async def get_prompt_input_template_by_id_route(
	prompt_input_template_id: UUID,
) -> PromptInputTemplate:
	"""
	Get a prompt input template by id
	"""
	response = get_prompt_input_template_by_id(
		prompt_input_template_id=prompt_input_template_id,
	)
	if response is None:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Prompt input template not found"
		)
	return response


@router.post(
	"/prompt_input_templates",
	status_code=status.HTTP_201_CREATED,
	dependencies=[Depends(AuthBearer())])
async def create_prompt_input_template_route(
	prompt_input_template: PromptInputTemplateProperties,
	prompt_id: UUID = Query(..., description="The ID of the prompt")
) -> PromptInputTemplate:
	"""
	Create a prompt input template
	"""
	return create_prompt_input_template_by_prompt_id(
		prompt_id=prompt_id,
		prompt_input_template=prompt_input_template
	)

@router.put(
	"/prompt_input_templates/{prompt_input_template_id}",
	status_code=status.HTTP_201_CREATED,
	dependencies=[Depends(AuthBearer())])
async def update_prompt_input_template_route(
	prompt_input_template_id: UUID,
	prompt_input_template: PromptInputTemplateProperties,
) -> PromptInputTemplate:
	"""
	Update a prompt input template
	"""
	response = update_prompt_input_template_by_id(
		prompt_input_template_id=prompt_input_template_id,
		prompt_input_template=prompt_input_template
	
	)
	if response is None:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Prompt input template not found"
		)
	return response

@router.delete(
	"/prompt_input_templates/{prompt_input_template_id}",
	status_code=status.HTTP_200_OK,
	dependencies=[Depends(AuthBearer())])
async def delete_prompt_input_template_route(
	prompt_input_template_id: UUID,
) -> PromptInputTemplate:
	"""
	Delete a prompt input template
	"""
	response = delete_prompt_input_template_by_id(
		prompt_input_template_id=prompt_input_template_id,
	)
	if response is None:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Prompt input template not found"
		)
	return response

@router.get(
	"/prompt_output_templates",
	status_code=status.HTTP_200_OK,
	dependencies=[Depends(AuthBearer())])
async def get_all_prompt_output_template_by_prompt_id_route(
	prompt_id: UUID = Query(..., description="The ID of the prompt")
) -> List[PromptOutputTemplate]:
	"""
	Get a prompt output template by prompt id
	"""
	return get_all_prompt_output_template_by_prompt_id(prompt_id)

@router.get(
	"/prompt_output_templates/{prompt_output_template_id}",
	status_code=status.HTTP_200_OK,
	dependencies=[Depends(AuthBearer())])
async def get_prompt_output_template_by_id_route(
	prompt_output_template_id: UUID,
) -> PromptOutputTemplate:
	"""
	Get a prompt output template by id
	"""
	response = get_prompt_output_template_by_id(
		prompt_output_template_id=prompt_output_template_id,
	)
	if response is None:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Prompt output template not found"
		)
	return response

@router.post(
	"/prompt_output_templates",
	status_code=status.HTTP_201_CREATED,
	dependencies=[Depends(AuthBearer())])
async def create_prompt_output_template_route(
	prompt_output_template: PromptOutputTemplateProperties,
	prompt_id: UUID = Query(..., description="The ID of the prompt")
) -> PromptOutputTemplate:
	"""
	Create a prompt output template
	"""
	return create_prompt_output_template_by_prompt_id(
		prompt_id=prompt_id,
		prompt_output_template=prompt_output_template
	)

@router.put(
	"/prompt_output_templates/{prompt_output_template_id}",
	status_code=status.HTTP_201_CREATED,
	dependencies=[Depends(AuthBearer())])
async def update_prompt_output_template_route(
	prompt_output_template_id: UUID,
	prompt_output_template: PromptOutputTemplateProperties,
) -> PromptOutputTemplate:
	"""
	Update a prompt output template
	"""
	response = update_prompt_output_template_by_id(
		prompt_output_template_id=prompt_output_template_id,
		prompt_output_template=prompt_output_template
	
	)
	if response is None:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Prompt output template not found"
		)
	return response

@router.delete(
	"/prompt_output_templates/{prompt_output_template_id}",
	status_code=status.HTTP_200_OK,
	dependencies=[Depends(AuthBearer())])
async def delete_prompt_output_template_route(
	prompt_output_template_id: UUID,
) -> PromptOutputTemplate:
	"""
	Delete a prompt output template
	"""
	response = delete_prompt_output_template_by_id(
		prompt_output_template_id=prompt_output_template_id,
	)
	if response is None:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Prompt output template not found"
		)
	return response