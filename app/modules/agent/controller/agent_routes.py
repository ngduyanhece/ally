

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from modal import Function
from modal.functions import FunctionCall

from app.middlewares.auth.auth_bearer import AuthBearer, get_current_user
from app.middlewares.auth.brain_authorization import \
    validate_brain_authorization
from app.modules.agent.entity.agent import BrainAgentInput
from app.modules.brain.entity.brain import RoleEnum
from app.modules.brain.service.brain_service import BrainService
from app.modules.user.entity.user_identity import UserIdentity

agent_router = APIRouter()
brain_service = BrainService()

@agent_router.post(
	"/agent/chat/{chat_id}",
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
	brain_detail = brain_service.get_brain_details(brain_id)
	single_agent_chat = Function.lookup("single-agent-chat", "single_agent_chat")
	try:
		call = single_agent_chat.spawn(chat_id, brain_detail, input)
		return {"call_id": call.object_id}
	except HTTPException as e:
		raise e
	
@agent_router.get(
	"/modal/{call_id}",
	dependencies=[
		Depends(
			AuthBearer(),
		),
	],
)
async def get_modal_results(call_id: str):
	function_call = FunctionCall.from_id(call_id)
	try:
		result = function_call.get(timeout=0)
	except TimeoutError:
		return JSONResponse(content="", status_code=202)
	return result