from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from modal import Function

from app.auth.auth_bearer import AuthBearer, get_current_user
from app.logger import get_logger
from app.models.chats import BrainAgentInput
from app.modules.user.entity.user_identity import UserIdentity
from app.repository.brain.get_brain_details import get_brain_details
from app.routes.authorizations.brain_authorization import \
    validate_brain_authorization
from app.routes.authorizations.types import RoleEnum

router = APIRouter()
logger = get_logger(__name__)

@router.get("/brain/chat/healthz", tags=["Health"])
async def healthz():
		return {"status": "ok"}


@router.post(
	"/brain/chat/{chat_id}",
	dependencies=[
		Depends(
			AuthBearer(),
		),
	]
)
async def create_brain_input_handler(
	chat_id: UUID,
	input: BrainAgentInput,
	brain_id: UUID = Query(..., description="The ID of the brain"),
	current_user: UserIdentity = Depends(get_current_user),
):
	"""
	Add a new question to the chat.
	"""
	validate_brain_authorization(
		brain_id=brain_id,
		user_id=current_user.id,
		required_roles=[RoleEnum.Viewer, RoleEnum.Editor, RoleEnum.Owner],
	)
	brain_detail = get_brain_details(brain_id)
	single_agent_chat = Function.lookup("single-agent-chat", "single_agent_chat")
	try:
		call = single_agent_chat.spawn(chat_id, brain_detail, input)
		return {"call_id": call.object_id}
	except HTTPException as e:
		raise e