

from uuid import UUID

from fastapi import APIRouter, Depends

from app.middlewares.auth.auth_bearer import AuthBearer
from app.modules.notification.entity.notification import Notification
from app.modules.notification.service.notification_service import \
    NotificationService

notification_router = APIRouter()
notification_service = NotificationService()

@notification_router.get(
		"/notifications/{chat_id}",
		dependencies=[Depends(AuthBearer())],
		tags=["Notification"],
)
async def get_notifications(
		chat_id: UUID,
) -> list[Notification]:
	"""
	Get notifications by chat_id
	"""
	return notification_service.get_chat_notifications(chat_id)
