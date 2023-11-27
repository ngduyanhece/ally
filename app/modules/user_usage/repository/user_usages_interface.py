from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID


class UserUsagesInterface(ABC):
	@abstractmethod
	def create_user_daily_usage(
		self, user_id: UUID, user_email: str, date: datetime):
		pass