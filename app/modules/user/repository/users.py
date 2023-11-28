from app.modules.user.repository.users_interface import UsersInterface


class Users(UsersInterface):
	def __init__(self, supabase_client):
		self.db = supabase_client
	
	def sign_in_user(self, sign_in_data):
		return self.db.auth.sign_in_with_password(dict(sign_in_data))
