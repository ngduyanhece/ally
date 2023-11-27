from abc import ABC, abstractmethod

from app.modules.user.entity.user_identity import UserSignInProperties


class UsersInterface(ABC):
	@abstractmethod
	def sign_in_user(sign_in_data: UserSignInProperties):
		"""
		Sign in a user using their email and password.
		"""
		pass