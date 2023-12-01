from app.middlewares.auth.jwt_token_handler import create_access_token
from app.modules.user.repository.users_interface import UsersInterface


class Users(UsersInterface):
	def __init__(self, supabase_client):
		self.db = supabase_client
	
	def sign_in_user(self, sign_in_data):
		response = self.db.auth.sign_in_with_password(dict(sign_in_data))
		authentication_dict = response.session.user.identities[0].identity_data
		token = create_access_token(authentication_dict)
		return {"token": token, "user": authentication_dict}
	