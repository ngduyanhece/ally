

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from modal import Function
from modal.functions import FunctionCall

from app.llm.brain_agent import BrainAgent
from app.middlewares.auth.auth_bearer import AuthBearer, get_current_user
from app.middlewares.auth.brain_authorization import \
    validate_brain_authorization
from app.modules.agent.entity.agent import BrainAgentInput
from app.modules.brain.entity.brain import RoleEnum
from app.modules.brain.service.brain_service import BrainService
from app.modules.test_data.service.test_data_service import TestDataService
from app.modules.user.entity.user_identity import UserIdentity

agent_router = APIRouter()
brain_service = BrainService()
test_data_service = TestDataService()

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
	brain_details = brain_service.get_brain_details(brain_id)
	# single_agent_chat = Function.lookup("single-agent-chat", "single_agent_chat")
	# try:
	# 	call = single_agent_chat.spawn(chat_id, brain_details, input)
	# 	return {"call_id": call.object_id}
	# except HTTPException as e:
	# 	raise e
	brain_agent = BrainAgent(
		brain_details=brain_details
	)
	answer = brain_agent.generate_answer(chat_id=chat_id, input=input)
	return answer

@agent_router.post(
	"/agent/learn/{chat_id}",
	status_code=status.HTTP_201_CREATED,
	dependencies=[Depends(AuthBearer())],
)
async def run_brain_learning_process(
	chat_id: UUID,
	brain_id: UUID = Query(..., description="The ID of the brain"),
	message_id: UUID = Query(..., description="The ID of message"),
	current_user: UserIdentity = Depends(get_current_user),
):
	validate_brain_authorization(
		brain_id=brain_id,
		user_id=current_user.id,
		required_roles=[RoleEnum.Viewer, RoleEnum.Editor, RoleEnum.Owner],
	)
	brain_details = brain_service.get_brain_details(brain_id)
	test_data = test_data_service.create_testcase_data_from_message(
		message_id, str(message_id))
	single_agent_learn = Function.lookup(
		"single-agent-learn", "single_agent_learn")
	try:
		call = single_agent_learn.spawn(
			chat_id, test_data.testcase_data_id, brain_details)
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