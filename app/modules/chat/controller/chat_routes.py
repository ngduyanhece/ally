# get all chats
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.middlewares.auth.auth_bearer import AuthBearer, get_current_user
from app.modules.chat.entity.chat import (Chat, CreateChatProperties,
                                          GetChatHistoryOutput)
from app.modules.chat.service.chat_service import ChatService
from app.modules.user.entity.user_identity import UserIdentity

chat_router = APIRouter()

chat_service = ChatService()

@chat_router.get("/chat/healthz", tags=["Health"])
async def healthz():
		return {"status": "ok"}

@chat_router.get("/chats", dependencies=[Depends(AuthBearer())])
async def get_chats(
	current_user: UserIdentity = Depends(get_current_user)
) -> list[Chat]:
	"""
	Retrieve all chats for the current user.

	- `current_user`: The current authenticated user.
	- Returns a list of all chats for the user.

	This endpoint retrieves all the chats associated with the current authenticated user. It returns a list of chat objects
	containing the chat ID and chat name for each chat.
	"""
	chats = chat_service.get_user_chats(str(current_user.id))
	return chats

# create new chat
@chat_router.post("/chats", dependencies=[Depends(AuthBearer())])
async def create_chat_handler(
	chat_data: CreateChatProperties,
	current_user: UserIdentity = Depends(get_current_user),
):
	"""
	Create a new chat with initial chat messages.
	"""

	return chat_service.create_chat(user_id=current_user.id, chat_data=chat_data)


# update existing chat metadata
@chat_router.put(
	"/chats/{chat_id}", dependencies=[Depends(AuthBearer())]
)
async def update_chat_metadata_handler(
	chat_data: CreateChatProperties,
	chat_id: UUID,
	current_user: UserIdentity = Depends(get_current_user),
) -> Chat:
	"""
	Update chat attributes
	"""
	try:
		chat = chat_service.get_chat_by_id(chat_id)
	except Exception as e:
		raise HTTPException(status_code=400, detail="chat not found")
	if str(current_user.id) != chat.user_id:
		raise HTTPException(
			status_code=403,  
			detail="You should be the owner of the chat to update it.",
		)
	return chat_service.update_chat(chat_id=chat_id, chat_data=chat_data)

# delete one chat
@chat_router.delete(
	"/chats/{chat_id}", dependencies=[Depends(AuthBearer())]
)
async def delete_chat(chat_id: UUID) -> Chat:
	"""
	Delete a specific chat by chat ID.
	"""
	# remove_chat_notifications(chat_id)
	try:
		chat = chat_service.delete_chat(chat_id)
		return chat
	except Exception as e:
		raise HTTPException(status_code=400, detail="chat not found")

@chat_router.get(
    "/chats/{chat_id}/history", dependencies=[Depends(AuthBearer())]
)
async def get_chat_history_handler(
    chat_id: UUID,
) -> list[GetChatHistoryOutput]:
    # TODO: RBAC with current_user
    return chat_service.get_chat_history(chat_id)