from datetime import datetime
from uuid import UUID

from app.logger import get_logger
from app.models.settings import get_supabase_client
from app.modules.user_usage.repository.user_usages import UserUsages

logger = get_logger(__name__)

class UserUsageService:
	daily_requests_count: int = 0
	repository = UserUsages

	def __init__(self):
		supabase_client = get_supabase_client()
		self.repository = UserUsages(supabase_client)
	
	def get_user_usage(self, user_id: UUID):
		"""
		Fetch the user request stats from the database
		"""
		request = self.repository.get_user_usage(user_id)

		return request

	def get_user_settings(self, user_id: UUID):
		"""
		Fetch the user settings from the database
		"""
		request = self.repository.get_user_settings(user_id)

		return request

	def handle_increment_user_request_count(self, user_id: UUID, email, date: datetime):
		"""
		Increment the user request count in the database
		"""
		current_requests_count = self.repository.get_user_requests_count_for_day(
			user_id, date
		)

		if current_requests_count is None:
			if email is None:
				raise ValueError("User Email should be defined for daily usage table")
			self.repository.create_user_daily_usage(
					user_id=user_id, date=date, user_email=email
			)
			self.daily_requests_count = 1
			return

		self.repository.increment_user_request_count(
			user_id=user_id,
			date=date,
			current_requests_count=current_requests_count,
		)

		self.daily_requests_count = current_requests_count

		logger.info(
			f"User {email} request count updated to {current_requests_count}"
		)