from abc import ABC, abstractmethod

from app.modules.api_key.entity.api_key import ApiKey, ApiKeyInfo
from app.modules.user.entity.user_identity import UserIdentity


class APIKeysInterface(ABC):
	@abstractmethod
	def create_api_key(self, new_key_id: str, new_api_key: str, user_id: str, user_email: str) -> ApiKey:
		"""
		Create a new API key for the current user.
		"""
		pass

	def get_active_api_key(self, api_key: str):
		"""
		Get an active API key by key.
		"""
		pass
	
	def get_user_id_by_api_key(self, api_key: str):
		"""
		Get the user ID by API key.
		"""
		pass

	def get_user_email_by_api_key(self, api_key: str):
		"""
		Get the user email by API key.
		"""
		pass

	def delete_api_key(self, key_id: str, current_user: UserIdentity) -> None:
		"""
		Delete an API key by ID.
		"""
		pass

	def get_api_keys(self, current_user: UserIdentity) -> list[ApiKeyInfo]:
		"""
		Retrieve all API keys of the current user.
		"""
		pass

