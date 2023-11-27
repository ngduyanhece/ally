
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.params import Depends
from modal import Function

from app.auth.auth_bearer import AuthBearer, get_current_user
from app.logger import get_logger
from app.modules.user.entity.user_identity import UserIdentity
from app.repository.brain import get_brain_by_id
from app.routes.authorizations.brain_authorization import \
    validate_brain_authorization
from app.routes.authorizations.types import RoleEnum

router = APIRouter()
logger = get_logger(__name__)

@router.get("/learn/healthz", tags=["Health"])
async def healthz():
		return {"status": "ok"}

@router.post(
	"/learn/brain/{chat_id}",
	status_code=status.HTTP_201_CREATED,
	dependencies=[Depends(AuthBearer())],
)
async def run_brain_learning_process(
	chat_id: UUID,
	brain_id: UUID = Query(..., description="The ID of the brain"),
	testcase_data_id: UUID = Query(..., description="The ID of the dataset"),
	current_user: UserIdentity = Depends(get_current_user),
):
	validate_brain_authorization(
		brain_id=brain_id,
		user_id=current_user.id,
		required_roles=[RoleEnum.Viewer, RoleEnum.Editor, RoleEnum.Owner],
	)
	brain_details = get_brain_by_id(brain_id)
	single_agent_learn = Function.lookup(
		"single-agent-learn", "single_agent_learn")
	try:
		call = single_agent_learn.spawn(chat_id, testcase_data_id, brain_details)
		return {"call_id": call.object_id}
	except HTTPException as e:
		raise e

@router.post(
	"/batch_learn/brain/{chat_id}",
	status_code=status.HTTP_201_CREATED,
	dependencies=[Depends(AuthBearer())],
)
async def run_batch_learning_process(
	brain_id: UUID = Query(..., description="The ID of the brain"),
	dataset_id: UUID = Query(..., description="The ID of the dataset"),
	current_user: UserIdentity = Depends(get_current_user),
):
	validate_brain_authorization(
		brain_id=brain_id,
		user_id=current_user.id,
		required_roles=[RoleEnum.Viewer, RoleEnum.Editor, RoleEnum.Owner],
	)
	brain_details = get_brain_by_id(brain_id)
