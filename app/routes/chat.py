import time
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from modal import Function

from app.auth.auth_bearer import AuthBearer, get_current_user
from app.llm.llm_brain import LLMBrain
from app.llm.llm_meta_brain import LLMMetaBrain
from app.llm.utils.get_brains_infos_for_meta_brain import \
    get_brain_infos_for_meta_brain
from app.models.brain_entity import BrainEntity
from app.models.brains import Brain
from app.models.chats import ChatInput, MetaChatInput
from app.models.databases.supabase.supabase import SupabaseDB
from app.models.meta_brain_entity import MetaBrainEntity
from app.models.settings import get_supabase_db
from app.models.user_usage import UserUsage
from app.modules.user.entity.user_identity import UserIdentity
from app.modules.user.repository.get_user_identity import get_user_identity
from app.repository.brain.get_brain_details import get_brain_details
from app.repository.chat.get_chat_history_with_notifications import (
    ChatItem, get_chat_history_with_notifications)
from app.repository.meta_brain.get_meta_brain_details import \
    get_meta_brain_details
from app.repository.notification.remove_chat_notifications import \
    remove_chat_notifications
from app.routes.authorizations.brain_authorization import \
    validate_brain_authorization
from app.routes.authorizations.meta_brain_authorization import \
    validate_meta_brain_authorization
from app.routes.authorizations.types import RoleEnum

router = APIRouter()

class NullableUUID(UUID):
	@classmethod
	def __get_validators__(cls):
		yield cls.validate

	@classmethod
	def validate(cls, v) -> UUID | None:
		if v == "":
			return None
		try:
			return UUID(v)
		except ValueError:
			return None
	

def delete_chat_from_db(supabase_db: SupabaseDB, chat_id):
	try:
		supabase_db.delete_chat_history(chat_id)
	except Exception as e:
		print(e)
		pass
	try:
		supabase_db.delete_chat(chat_id)
	except Exception as e:
		print(e)
		pass


def check_user_requests_limit(
	user: UserIdentity,
):
	userDailyUsage = UserUsage(
		id=user.id, email=user.email, openai_api_key=user.openai_api_key
	)

	userSettings = userDailyUsage.get_user_settings()

	date = time.strftime("%Y%m%d")
	userDailyUsage.handle_increment_user_request_count(date)

	if user.openai_api_key is None:
		daily_chat_credit = userSettings.get("daily_chat_credit", 0)
		if int(userDailyUsage.daily_requests_count) >= int(daily_chat_credit):
			raise HTTPException(
				status_code=429,  # pyright: ignore reportPrivateUsage=none
				detail="You have reached the maximum number of requests for today.",  # pyright: ignore reportPrivateUsage=none
			)
	else:
		pass

# delete one chat
@router.delete(
	"/chats/{chat_id}", dependencies=[Depends(AuthBearer())]
)
async def delete_chat(chat_id: UUID):
	"""
	Delete a specific chat by chat ID.
	"""
	supabase_db = get_supabase_db()
	remove_chat_notifications(chat_id)

	delete_chat_from_db(supabase_db=supabase_db, chat_id=chat_id)
	return {"message": f"{chat_id}  has been deleted."}

# add new input to brain to chat
@router.post(
	"/chat/brain/{chat_id}/question",
	dependencies=[
		Depends(
			AuthBearer(),
		),
	],
)
async def create_brain_chat_input_handler(
	request: Request,
	chat_input: ChatInput,
	chat_id: UUID,
	brain_id: UUID = Query(..., description="The ID of the brain"),
	current_user: UserIdentity = Depends(get_current_user),
):
	"""
	Add a new question to the chat.
	"""
	if brain_id:
		validate_brain_authorization(
			brain_id=brain_id,
			user_id=current_user.id,
			required_roles=[RoleEnum.Viewer, RoleEnum.Editor, RoleEnum.Owner],
		)
	# Retrieve user's OpenAI API key
	current_user.openai_api_key = request.headers.get("Openai-Api-Key")
	brain = Brain(id=brain_id)
	brain_details: BrainEntity | None = None
	userDailyUsage = UserUsage(
		id=current_user.id,
		email=current_user.email,
		openai_api_key=current_user.openai_api_key,
	)
	userSettings = userDailyUsage.get_user_settings()
	is_model_ok = (brain_details or chat_input).model in userSettings.get("models", ["gpt-3.5-turbo"])  # type: ignore
	if not current_user.openai_api_key and brain_id:
		brain_details = get_brain_details(brain_id)
		if brain_details:
			current_user.openai_api_key = brain_details.openai_api_key

	if not current_user.openai_api_key:
		user_identity = get_user_identity(current_user.id, current_user.email)

		if user_identity is not None:
			current_user.openai_api_key = user_identity.openai_api_key
	
	if (
		not chat_input.model
		or not chat_input.temperature
		or not chat_input.max_tokens
	):
		# TODO: create ChatConfig class (pick config from brain or user or chat) and use it here
		chat_input.model = chat_input.model or brain.model or "gpt-3.5-turbo"
		chat_input.temperature = (
			chat_input.temperature or brain.temperature or 0.1
		)
		chat_input.max_tokens = chat_input.max_tokens or brain.max_tokens or 256
	
	try:
		# TODO: improve the user request limit 
		# check_user_requests_limit(current_user)
		is_model_ok = (brain_details or chat_input).model in userSettings.get("models", ["gpt-3.5-turbo"])  # type: ignore
		model = chat_input.model if is_model_ok else brain_details.model
		max_tokens = chat_input.max_tokens if chat_input.max_tokens else brain_details.max_tokens
		temperature = chat_input.temperature if chat_input.temperature else brain_details.temperature
		user_openai_api_key = current_user.openai_api_key
		brain_chat = Function.lookup("brain-chat", "brain_chat")
		call = brain_chat.spawn(
			chat_id=str(chat_id),
			model=model,
			max_tokens=max_tokens,
			temperature=temperature,
			brain_id=str(brain_id),
			user_openai_api_key=user_openai_api_key,
			prompt_id=str(chat_input.prompt_id),
			chat_input=chat_input,
		)
		# llm_brain = LLMBrain(
		# 		chat_id=str(chat_id),
		# 		model=chat_input.model if is_model_ok else brain_details.model,  # type: ignore
		# 		max_tokens=chat_input.max_tokens if chat_input.max_tokens else brain_details.max_tokens,
		# 		temperature=chat_input.temperature if chat_input.temperature else brain_details.temperature,
		# 		brain_id=str(brain_id),
		# 		user_openai_api_key=current_user.openai_api_key,  # pyright: ignore reportPrivateUsage=none
		# 		prompt_id=str(chat_input.prompt_id),
		# )
		# chat_answer = llm_brain.generate_answer(chat_id, chat_input)
		return {"call_id": call.object_id}
	except HTTPException as e:
		raise e
	
@router.post(
	"/metabrain/chat/{chat_id}/question",
	dependencies=[
		Depends(
			AuthBearer(),
		),
	],
)
async def create_meta_brain_chat_input_handler(
	request: Request,
	chat_input: MetaChatInput,
	chat_id: UUID,
	meta_brain_id: UUID = Query(..., description="The ID of the meta brain"),
	current_user: UserIdentity = Depends(get_current_user),
):
	"""
	Add a new question to the meta brain to chat.
	"""
	if meta_brain_id:
		validate_meta_brain_authorization(
			meta_brain_id=meta_brain_id,
			user_id=current_user.id,
			required_roles=[RoleEnum.Viewer, RoleEnum.Editor, RoleEnum.Owner],
		)
	current_user.openai_api_key = request.headers.get("Openai-Api-Key")
	meta_brain_details: MetaBrainEntity | None = None
	userDailyUsage = UserUsage(
		id=current_user.id,
		email=current_user.email,
		openai_api_key=current_user.openai_api_key,
	)
	userSettings = userDailyUsage.get_user_settings()
	if not current_user.openai_api_key and meta_brain_id:
		meta_brain_details = get_meta_brain_details(meta_brain_id)
		if meta_brain_details:
			current_user.openai_api_key = meta_brain_details.openai_api_key

	if not current_user.openai_api_key:
		user_identity = get_user_identity(current_user.id, current_user.email)

		if user_identity is not None:
			current_user.openai_api_key = user_identity.openai_api_key
	
	if (
		not chat_input.model or not chat_input.temperature
			or not chat_input.max_tokens
	):
		chat_input.model = chat_input.model or meta_brain_details.model or "gpt-3.5-turbo"
		chat_input.temperature = (
			chat_input.temperature or meta_brain_details.temperature or 0.1
		)
		chat_input.max_tokens = chat_input.max_tokens or meta_brain_details.max_tokens or 256
	
	is_model_ok = (meta_brain_details or chat_input).model in userSettings.get("models", ["gpt-3.5-turbo"])  # type: ignore
	llm_meta_brain = LLMMetaBrain(
		chat_id=str(chat_id),
		model=chat_input.model if is_model_ok else "gpt-3.5-turbo",  # type: ignore
		max_tokens=chat_input.max_tokens,
		temperature=chat_input.temperature,
		meta_brain_id=str(meta_brain_id),
		user_openai_api_key=current_user.openai_api_key,
		brains_infos=get_brain_infos_for_meta_brain(meta_brain_id, str(chat_id)),
	)
	chat_answer = llm_meta_brain.generate_answer(chat_id, chat_input)
	return chat_answer

# stream new question response from chat
@router.post(
	"/brain/chat/{chat_id}/question/stream",
	dependencies=[
		Depends(
			AuthBearer(),
		),
	]
)
async def create_stream_question_handler(
	request: Request,
	chat_input: ChatInput,
	chat_id: UUID,
	brain_id: UUID = Query(..., description="The ID of the brain"),
	current_user: UserIdentity = Depends(get_current_user),
) -> StreamingResponse:
	"""
	Add a new question to the chat.
	"""
	if brain_id:
		validate_brain_authorization(
			brain_id=brain_id,
			user_id=current_user.id,
			required_roles=[RoleEnum.Viewer, RoleEnum.Editor, RoleEnum.Owner],
		)
	 # Retrieve user's OpenAI API key
	current_user.openai_api_key = request.headers.get("Openai-Api-Key")
	brain = Brain(id=brain_id)
	brain_details: BrainEntity | None = None
	userDailyUsage = UserUsage(
		id=current_user.id,
		email=current_user.email,
		openai_api_key=current_user.openai_api_key,
	)
	userSettings = userDailyUsage.get_user_settings()
	is_model_ok = (brain_details or chat_input).model in userSettings.get("models", ["gpt-3.5-turbo"])  # type: ignore
	if not current_user.openai_api_key and brain_id:
		brain_details = get_brain_details(brain_id)
		if brain_details:
			current_user.openai_api_key = brain_details.openai_api_key

	if not current_user.openai_api_key:
		user_identity = get_user_identity(current_user.id, current_user.email)

		if user_identity is not None:
			current_user.openai_api_key = user_identity.openai_api_key
	
	if (
		not chat_input.model
		or not chat_input.temperature
		or not chat_input.max_tokens
	):
		# TODO: create ChatConfig class (pick config from brain or user or chat) and use it here
		chat_input.model = chat_input.model or brain.model or "gpt-3.5-turbo"
		chat_input.temperature = (
			chat_input.temperature or brain.temperature or 0.1
		)
		chat_input.max_tokens = chat_input.max_tokens or brain.max_tokens or 256
	
	try:
		#TODO: improve the user request limit 
		# check_user_requests_limit(current_user)
		is_model_ok = (brain_details or chat_input).model in userSettings.get("models", ["gpt-3.5-turbo"])  # type: ignore
		llm_brain = LLMBrain(
				chat_id=str(chat_id),
				model=chat_input.model if is_model_ok else "gpt-3.5-turbo",  # type: ignore
				max_tokens=chat_input.max_tokens,
				temperature=chat_input.temperature,
				brain_id=str(brain_id),
				user_openai_api_key=current_user.openai_api_key,  # pyright: ignore reportPrivateUsage=none
				prompt_id=str(chat_input.prompt_id),
		)
		return StreamingResponse(
			llm_brain.generate_answer_stream(chat_id, chat_input),
			media_type="text/event-stream",
		)

	except HTTPException as e:
		raise e

# get chat history
@router.get(
	"/chats/{chat_id}/history", dependencies=[Depends(AuthBearer())]
)
async def get_chat_history_handler(
	chat_id: UUID,
) -> List[ChatItem]:
	# TODO: RBAC with current_user
	return get_chat_history_with_notifications(chat_id)

