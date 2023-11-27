from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.params import Depends

from app.auth.auth_bearer import AuthBearer, get_current_user
from app.logger import get_logger
from app.models.chats import MessageLabel, MessageLabelOutput
from app.modules.user.entity.user_identity import UserIdentity
from app.repository.chat.create_message_label_by_id import \
    crate_message_label_by_id
from app.repository.chat.delete_message_label_by_id import \
    delete_message_label_by_id
from app.repository.chat.get_message_label_by_id import get_message_label_by_id
from app.repository.chat.update_message_label_by_id import \
    update_message_label_by_id

logger = get_logger(__name__)
router = APIRouter()

@router.get(
		"/label",
		status_code=status.HTTP_200_OK,
		dependencies=[Depends(AuthBearer())])
async def get_label_for_message_handler(
	message_id: UUID = Query(..., description="The ID of the message"),
) -> MessageLabelOutput:
	response = get_message_label_by_id(message_id)
	if response is None:
		raise HTTPException(status_code=404, detail="Label not found")
	return response


@router.post(
		"/label",
		status_code=status.HTTP_201_CREATED, 
		dependencies=[Depends(AuthBearer())])
async def create_label_for_message_handler(
	message_label: MessageLabel,
	message_id: UUID = Query(..., description="The ID of the message"),
	current_user: UserIdentity = Depends(get_current_user),
):
	try:
		response = crate_message_label_by_id(message_label, message_id, current_user.id)
		return response
	except Exception as e:
		return HTTPException(status_code=404, detail=str(e))
	
@router.put(
		"/label",
		status_code=status.HTTP_200_OK, 
		dependencies=[Depends(AuthBearer())])
async def update_label_for_message_handler( 
	message_label: MessageLabel,
	message_id: UUID = Query(..., description="The ID of the message"),
	current_user: UserIdentity = Depends(get_current_user),
):
	try:
		response = update_message_label_by_id(message_label, message_id, current_user.id)
		return response
	except Exception as e:
		return HTTPException(status_code=404, detail=str(e))
	
@router.delete(
		"/label",
		status_code=status.HTTP_200_OK, 
		dependencies=[Depends(AuthBearer())])
async def delete_label_for_message_handler(
	message_id: UUID = Query(..., description="The ID of the message"),
	current_user: UserIdentity = Depends(get_current_user),
):
	try:
		response = delete_message_label_by_id(message_id, current_user.id)
		return response
	except Exception as e:
		return HTTPException(status_code=404, detail=str(e))
