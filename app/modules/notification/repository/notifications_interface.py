from abc import ABC, abstractmethod

from app.modules.notification.entity.notification import (
    CreateNotificationProperties, Notification)


class NotificationsInterface(ABC):
	@abstractmethod
	def add_notification(
		self, notification: CreateNotificationProperties
	) -> Notification:
		"""
		Add a notification
		"""