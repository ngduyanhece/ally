from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import HTTPException
from modules.api_key.entity.api_key import ApiKey
from modules.api_key.repository.api_keys import ApiKeys
from modules.user.entity.user_identity import UserIdentity
from modules.user.service.user_service import UserService
from pydantic.v1 import DateError

user_service = UserService()

class APIKeyService:
	
	def __init__(self):
		self.repository = ApiKeys()
	
	def create_api_key(
		self, new_key_id, new_api_key, user_id, user_email) -> ApiKey:

		return self.repository.create_api_key(
			new_key_id, new_api_key, user_id, user_email)
	
	def delete_api_key(self, key_id: str, user_id: UUID):
		return self.repository.delete_api_key(key_id, user_id)
	
	def get_active_api_key(self, api_key: str):
		return self.repository.get_active_api_key(api_key)
	
	def get_user_id_by_api_key(self, api_key: str):
		return self.repository.get_user_id_by_api_key(api_key)
	
	def get_user_email_by_api_key(self, api_key: str):
		return self.repository.get_user_email_by_api_key(api_key)
	
	def get_user_api_keys(self, user_id: UUID) -> List[ApiKey]:
		return self.repository.get_user_api_keys(user_id)

	async def verify_api_key(self, api_key: str) -> bool:
		try:
			# Use UTC time to avoid timezone issues
			current_date = datetime.utcnow().date()
			result = self.repository.get_active_api_key(api_key)

			if result.data is not None and len(result.data) > 0:
				api_key_creation_date = datetime.strptime(
					result.data[0]["creation_time"], "%Y-%m-%dT%H:%M:%S"
				).date()

				if (api_key_creation_date.month == current_date.month) and (
					api_key_creation_date.year == current_date.year
				):
					return True
				return False
		except DateError:
			return False

	async def get_user_from_api_key(self, api_key: str) -> UserIdentity:
		user_id_data = self.repository.get_user_id_by_api_key(api_key)

		if not user_id_data.data:
			raise HTTPException(status_code=400, detail="Invalid API key.")

		user_id = user_id_data.data[0]["user_id"]

		# TODO: directly UserService instead
		email = user_service.get_user_email_by_user_id(user_id)

		if email is None:
			raise HTTPException(status_code=400, detail="Invalid API key.")

		return UserIdentity(email=email, id=user_id)
