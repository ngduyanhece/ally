from uuid import UUID

from fastapi import APIRouter, Depends

from app.auth.auth_bearer import AuthBearer
from app.repository.notification.get_chat_notifications import \
    get_chat_notifications

router = APIRouter()

@router.get(
    "/notifications/{chat_id}",
    dependencies=[Depends(AuthBearer())],
    tags=["Notification"],
)
async def get_notifications(
    chat_id: UUID,
):
    """
    Get notifications by chat_id
    """

    return get_chat_notifications(chat_id)