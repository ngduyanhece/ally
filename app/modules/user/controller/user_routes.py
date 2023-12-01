
from fastapi import APIRouter

from app.logger import get_logger
from app.modules.user.entity.user_identity import UserSignInProperties
from app.modules.user.service.user_service import UserService

user_router = APIRouter()

user_service = UserService()

logger = get_logger(__name__)

@user_router.post("/user")
def sign_in_route(
	sign_in_data: UserSignInProperties
):
	"""
	Sign in a user, just use for the backend development purpose.
	"""
	try:
		return user_service.sign_in_user(sign_in_data)
	except Exception as e:
		logger.error(f"Error signing in user: {e}")
		return {"error": "Error signing in user."}