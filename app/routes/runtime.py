from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.auth_bearer import AuthBearer, get_current_user
from app.models.databases.supabase.runtimes import CreateRuntimeProperties
from app.models.runtimes import RuntimeEntity
from app.modules.user.entity.user_identity import UserIdentity
from app.repository.runtime.delete_runtime_by_id import delete_runtime_by_id
from app.repository.runtime.get_runtime_by_id import get_runtime_by_id
from app.repository.runtime.get_user_runtimes import get_user_runtimes
from app.repository.runtime.update_runtime_by_id import update_runtime_by_id

router = APIRouter()

@router.get(
	"/runtimes",
	status_code=status.HTTP_200_OK,
	dependencies=[Depends(AuthBearer())])
async def get_runtimes(
	current_user: UserIdentity = Depends(get_current_user),
) -> list[RuntimeEntity]:
	"""
	Retrieve all runtimes of the current user
	"""
	return get_user_runtimes(current_user.id)

@router.post(
	"/runtimes",
	status_code=status.HTTP_201_CREATED,
	dependencies=[Depends(AuthBearer())])
async def create_prompt_route(
	runtime: CreateRuntimeProperties,
	current_user: UserIdentity = Depends(get_current_user)
) -> RuntimeEntity:
	"""
	Create a prompt for the current user
	"""
	try:
		response = create
		
		
		
		
		
		_runtime(runtime, current_user.id)
		return response
	except Exception as e:
		raise HTTPException(status_code=400, detail=str(e))

@router.get(
	"/runtimes/{runtime_id}",
	status_code=status.HTTP_200_OK,
	dependencies=[Depends(AuthBearer())])
async def get_runtime(
	runtime_id: str,
) -> RuntimeEntity:
	"""
	Retrieve a runtime by ID
	"""
	try:
		response = get_runtime_by_id(runtime_id)
		return response
	except Exception as e:
		raise HTTPException(status_code=400, detail=str(e))
	
@router.put(
	"/runtimes/{runtime_id}",
	status_code=status.HTTP_200_OK,
	dependencies=[Depends(AuthBearer())])
async def update_runtime(
	runtime_id: UUID,
	runtime: CreateRuntimeProperties,
) -> RuntimeEntity:
	"""
	Update a runtime by ID
	"""
	try:
		response = update_runtime_by_id(
			runtime_id=runtime_id,
			runtime=runtime
		)
		return response
	except Exception as e:
		raise HTTPException(status_code=400, detail=str(e))

@router.delete(
	"/runtimes/{runtime_id}",
	status_code=status.HTTP_200_OK,
	dependencies=[Depends(AuthBearer())])
async def delete_runtime(
	runtime_id: UUID,
) -> RuntimeEntity:
	"""
	Delete a runtime by ID
	"""
	try:
		response = delete_runtime_by_id(
			runtime_id=runtime_id
		)
		return response
	except Exception as e:
		raise HTTPException(status_code=400, detail=str(e))