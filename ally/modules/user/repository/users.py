from ally.core.settings import get_supabase_client
from ally.logger import get_logger
from ally.middlewares.auth.jwt_token_handler import create_access_token
from ally.modules.user.dto.inputs import UserSignInProperties
from ally.modules.user.entity.user_identity import UserIdentity
from ally.modules.user.repository.users_interface import UsersInterface

logger = get_logger(__name__)

class Users(UsersInterface):
	def __init__(self):
		supabase_client = get_supabase_client()
		self.db = supabase_client
	
	def sign_in_user(self, sign_in_data: UserSignInProperties):
		response = self.db.auth.sign_in_with_password(dict(sign_in_data))
		authentication_dict = response.session.user.identities[0].identity_data
		token = create_access_token(authentication_dict)
		return {"token": token, "user": authentication_dict}
	
	def create_user_identity(self, id):
		response = (
			self.db.from_("user_identity")
			.insert(
				{
					"user_id": str(id),
				}
			)
			.execute()
		)
		user_identity = response.data[0]
		return UserIdentity(id=user_identity.get("user_id"))

	def update_user_properties(
		self,
		user_id,
		user_identity_updatable_properties,
	):
		response = (
			self.db.from_("user_identity")
			.update(user_identity_updatable_properties.__dict__)
			.filter("user_id", "eq", user_id)  # type: ignore
			.execute()
		)

		if len(response.data) == 0:
			return self.create_user_identity(user_id)

		user_identity = response.data[0]

		print("USER_IDENTITY", user_identity)
		return UserIdentity(id=user_id)

	def get_user_identity(self, user_id):
		response = (
			self.db.from_("user_identity")
			.select("*")
			.filter("user_id", "eq", str(user_id))
			.execute()
		)

		if len(response.data) == 0:
			return self.create_user_identity(user_id)
		logger.info("USER_IDENTITY: %s", response.data[0])
		user_identity = response.data[0]
		return UserIdentity(
			id=user_identity.get("user_id"),
			email=user_identity.get("email"),
		)

	def get_user_id_by_user_email(self, email):
		response = (
			self.db.rpc("get_user_id_by_user_email", {"user_email": email})
			.execute()
			.data
		)
		if len(response) > 0:
			return response[0]["user_id"]
		return None

	def get_user_email_by_user_id(self, user_id):
		response = self.db.rpc(
				"get_user_email_by_user_id", {"user_id": str(user_id)}
		).execute()
		return response.data[0]["email"]
