from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class NotificationsStatusEnum(str, Enum):
	Pending = "Pending"
	Done = "Done"

class CreateNotificationProperties(BaseModel):
	"""Properties that can be received on notification creation"""

	chat_id: Optional[UUID] = None
	message: Optional[str] = None
	action: str
	status: NotificationsStatusEnum = NotificationsStatusEnum.Pending

	def dict(self, *args, **kwargs):
		notification_dict = super().model_dump(*args, **kwargs)
		if notification_dict.get("chat_id"):
				notification_dict["chat_id"] = str(notification_dict.get("chat_id"))
		return notification_dict


class DeleteNotificationResponse(BaseModel):
	"""Response when deleting a prompt"""

	status: str = "delete"
	notification_id: UUID


class UpdateNotificationProperties(BaseModel):
	"""Properties that can be received on notification update"""

	message: Optional[str]
	status: Optional[NotificationsStatusEnum] = NotificationsStatusEnum.Done


class Notification(BaseModel):
	id: UUID
	datetime: str
	chat_id: Optional[UUID]
	message: Optional[str]
	action: str
	status: NotificationsStatusEnum

	def dict(self, *args, **kwargs):
		notification_dict = super().model_dump(*args, **kwargs)
		if notification_dict.get("chat_id"):
			notification_dict["chat_id"] = str(notification_dict.get("chat_id"))
		return notification_dict
