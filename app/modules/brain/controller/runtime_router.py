
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.middlewares.auth.auth_bearer import AuthBearer
from app.modules.brain.entity.brain import (CreateRuntimeProperties,
                                            RuntimeEntity)
from app.modules.brain.service.brain_service import BrainService

runtime_router = APIRouter()

brain_Service = BrainService()

# update brain runtime
@runtime_router.put(
	"/runtimes/{runtime_id}",
	status_code=status.HTTP_200_OK,
	dependencies=[Depends(AuthBearer())])
async def update_runtime(
	runtime_id: UUID,
	runtime: CreateRuntimeProperties,
) -> RuntimeEntity:
	try:
		response = brain_Service.update_runtime_by_id(
			runtime_id=runtime_id,
			runtime=runtime
		)
		return response
	except Exception as e:
		raise HTTPException(status_code=400, detail=str(e))