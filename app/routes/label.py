from uuid import UUID

from fastapi import APIRouter, HTTPException, Query
from fastapi.params import Depends

from app.auth.auth_bearer import AuthBearer, get_current_user
from app.models.chats import MessageLabel, MessageLabelOutput
from app.models.user_identity import UserIdentity
from app.repository.chat.create_message_label_by_id import \
    crate_message_label_by_id
from app.repository.chat.delete_message_label_by_id import \
    delete_message_label_by_id
from app.repository.chat.get_message_label_by_id import get_message_label_by_id
from app.repository.chat.update_message_label_by_id import \
    update_message_label_by_id

router = APIRouter()

@router.get("/label", dependencies=[Depends(AuthBearer())])
async def get_label_for_message_handler(
    message_id: UUID = Query(..., description="The ID of the message"),
) -> MessageLabelOutput | None:
    return get_message_label_by_id(message_id)

@router.post("/label", dependencies=[Depends(AuthBearer())])
async def create_label_for_message_handler(
    message_label: MessageLabel,
    message_id: UUID = Query(..., description="The ID of the message"),
    current_user: UserIdentity = Depends(get_current_user),
):
    try:
        _ = crate_message_label_by_id(message_label, message_id, current_user.id)
        return HTTPException(status_code=201, detail="Label created")
    except Exception as e:
        return HTTPException(status_code=404, detail=str(e))
    
@router.put("/label", dependencies=[Depends(AuthBearer())])
async def update_label_for_message_handler( 
    message_label: MessageLabel,
    message_id: UUID = Query(..., description="The ID of the message"),
    current_user: UserIdentity = Depends(get_current_user),
):
    try:
        _ = update_message_label_by_id(message_label, message_id, current_user.id)
        return HTTPException(status_code=200, detail="Label updated")
    except Exception as e:
        return HTTPException(status_code=404, detail=str(e))
    
@router.delete("/label", dependencies=[Depends(AuthBearer())])
async def delete_label_for_message_handler(
    message_id: UUID = Query(..., description="The ID of the message"),
    current_user: UserIdentity = Depends(get_current_user),
):
    try:
        _ = delete_message_label_by_id(message_id, current_user.id)
        return HTTPException(status_code=200, detail="Label deleted")
    except Exception as e:
        return HTTPException(status_code=404, detail=str(e))
