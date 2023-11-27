from app.models.settings import get_supabase_client
from app.modules.user.entity.user_identity import UserSignInProperties
from app.modules.user.repository.users import Users


class UserService:
	repository = Users

	def __init__(self):
		supabase_client = get_supabase_client()
		self.repository = Users(supabase_client)
	
	def sign_in_user(self, sign_in_data: UserSignInProperties):
  		return self.repository.sign_in_user(sign_in_data)
