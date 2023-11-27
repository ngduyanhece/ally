from uuid import UUID

from app.models.settings import get_supabase_client
from app.modules.api_key.entity.api_key import ApiKey
from app.modules.api_key.repository.api_keys import APIKeys


class APIKeyService:
	repository: APIKeys
	
	def __init__(self):
		supabase_client = get_supabase_client()
		self.repository = APIKeys(supabase_client)
	
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
	
	def get_user_api_keys(self, user_id: UUID):
		return self.repository.get_user_api_keys(user_id)