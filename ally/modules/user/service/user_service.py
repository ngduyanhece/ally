from uuid import UUID

from modules.user.dto.inputs import UserSignInProperties
from modules.user.repository.users import Users


class UserService:
  	
	def __init__(self):
		self.repository = Users()
	
	def sign_in_user(self, sign_in_data: UserSignInProperties):
			return self.repository.sign_in_user(sign_in_data)
	
	def get_user_id_by_email(self, email: str) -> UUID | None:
		return self.repository.get_user_id_by_user_email(email)

	def get_user_email_by_user_id(self, user_id: UUID) -> str | None:
		return self.repository.get_user_email_by_user_id(user_id)
	
	def update_user_properties(
		self,
		user_id: UUID,
		user_identity_updatable_properties,
	):
		return self.repository.update_user_properties(
			user_id, user_identity_updatable_properties
		)
	
	def get_user_identity(self, user_id: UUID):
		return self.repository.get_user_identity(user_id)
