from uuid import UUID

from app.models.settings import get_supabase_client
from app.modules.notification.entity.notification import (
    CreateNotificationProperties, Notification, UpdateNotificationProperties)
from app.modules.notification.repository.notifications import Notifications


class NotificationService:
	repository: Notifications 

	def __init__(self):
		supabase_client = get_supabase_client()
		self.repository = Notifications(supabase_client)

	def add_notification(self, notification: CreateNotificationProperties):
		return self.repository.add_notification(notification)
	
	def get_chat_notifications(self, chat_id: UUID) -> list[Notification]:
		return self.repository.get_notifications_by_chat_id(chat_id)
	
	def remove_chat_notifications(self, chat_id: UUID) -> None:
		return self.repository.remove_notifications_by_chat_id(chat_id)
	
	def update_notification_by_id(
		self, notification_id, notification: UpdateNotificationProperties):
		return self.repository.update_notification_by_id(
			notification_id, notification)
