from uuid import UUID

from fastapi import HTTPException

from app.modules.notification.entity.notification import (
    CreateNotificationProperties, DeleteNotificationResponse, Notification,
    UpdateNotificationProperties)
from app.modules.notification.repository.notifications_interface import \
    NotificationsInterface


class Notifications(NotificationsInterface):
	def __init__(self, supabase_client):
		self.db = supabase_client

	def add_notification(
		self, notification: CreateNotificationProperties
	) -> Notification:
		"""
		Add a notification
		"""
		response = (
			self.db.from_("notifications").insert(notification.dict()).execute()
		).data
		return Notification(**response[0])

	def update_notification_by_id(
		self, notification_id: UUID, notification: UpdateNotificationProperties
	) -> Notification:
		"""Update a notification by id"""
		response = (
			self.db.from_("notifications")
			.update(notification.dict(exclude_unset=True))
			.filter("id", "eq", notification_id)
			.execute()
		).data

		if response == []:
			raise HTTPException(404, "Notification not found")

		return Notification(**response[0])

	def remove_notification_by_id(
		self, notification_id: UUID
	) -> DeleteNotificationResponse:
		"""
		Remove a notification by id
		Args:
			notification_id (UUID): The id of the notification

		Returns:
			str: Status message
		"""
		response = (
			self.db.from_("notifications")
			.delete()
			.filter("id", "eq", notification_id)
			.execute()
			.data
		)

		if response == []:
			raise HTTPException(404, "Notification not found")

		return DeleteNotificationResponse(
			status="deleted", notification_id=notification_id
		)

	def remove_notifications_by_chat_id(self, chat_id: UUID) -> None:
		"""
		Remove all notifications for a chat
		Args:
				chat_id (UUID): The id of the chat
		"""
		(
			self.db.from_("notifications")
			.delete()
			.filter("chat_id", "eq", chat_id)
			.execute()
		).data

	def get_notifications_by_chat_id(self, chat_id: UUID) -> list[Notification]:
		"""
		Get all notifications for a chat
		Args:
			chat_id (UUID): The id of the chat

		Returns:
			list[Notification]: The notifications
		"""
		# two_minutes_ago = (datetime.now() - timedelta(minutes=2)).strftime(
		# 	"%Y-%m-%d %H:%M:%S.%f"
		# )

		notifications = (
			self.db.from_("notifications")
			.select("*")
			.filter("chat_id", "eq", chat_id)
			# .filter("datetime", "gt", two_minutes_ago)
			.execute()
		).data

		return [Notification(**notification) for notification in notifications]