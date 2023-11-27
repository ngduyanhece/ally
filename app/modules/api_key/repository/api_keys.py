
from datetime import datetime
from uuid import UUID

from app.modules.api_key.entity.api_key import ApiKey
from app.modules.api_key.repository.api_keys_interface import APIKeysInterface


class APIKeys(APIKeysInterface):
	def __init__(self, supabase_client):
		self.db = supabase_client

	def create_api_key(
			self, new_key_id, new_api_key, user_id, user_email) -> ApiKey:
		response = (
			self.db.table("api_keys")
			.insert(
				[
					{
						"id": str(new_key_id),
						"user_id": str(user_id),
						"api_key": str(new_api_key),
						"email": str(user_email),
						"creation_time": datetime.utcnow().strftime(
							"%Y-%m-%d %H:%M:%S"
						),
						"is_active": True,
					}
				]
			).execute()
		).data[0]

		return ApiKey(
			api_key=response["api_key"],
			id=response["id"],
		)

	def delete_api_key(self, key_id: str, user_id: UUID):
		return (
			self.db.table("api_keys")
			.update(
				{
					"is_active": False,
					"deleted_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
				}
			)
			.match({"id": key_id, "user_id": user_id})
			.execute()
		)

	def get_active_api_key(self, api_key: str):
		response = (
			self.db.table("api_keys")
			.select("api_key", "creation_time")
			.filter("api_key", "eq", api_key)
			.filter("is_active", "eq", True)
			.execute()
		)
		return response

	def get_user_id_by_api_key(self, api_key: str):
		response = (
			self.db.table("api_keys")
			.select("user_id")
			.filter("api_key", "eq", api_key)
			.execute()
		)
		return response
	
	def get_user_email_by_api_key(self, api_key: str):
		response = (
			self.db.table("api_keys")
			.select("email")
			.filter("api_key", "eq", api_key)
			.execute()
		)
		return response

	def get_user_api_keys(self, user_id: UUID):
		response = (
			self.db.table("api_keys")
			.select("id, creation_time")
			.filter("user_id", "eq", user_id)
			.filter("is_active", "eq", True)
			.execute()
		)
		return response.data
