
from fastapi import APIRouter, Depends

from ally.logger import get_logger
from ally.middlewares.auth.auth_bearer import AuthBearer, get_current_user
from ally.modules.user.dto.inputs import (UserSignInProperties,
                                          UserUpdatableProperties)
from ally.modules.user.entity.user_identity import UserIdentity
from ally.modules.user.service.user_service import UserService

logger = get_logger(__name__)

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

def update_user_identity_route(
    user_identity_updatable_properties: UserUpdatableProperties,
    current_user: UserIdentity = Depends(get_current_user),
) -> UserIdentity:
    """
    Update user identity.
    """
    return user_service.update_user_properties(
        current_user.id, user_identity_updatable_properties
    )

@user_router.get(
    "/user/identity",
    dependencies=[Depends(AuthBearer())],
    tags=["User"],
)
def get_user_identity_route(
    current_user: UserIdentity = Depends(get_current_user),
) -> UserIdentity:
    """
    Get user identity.
    """
    return user_service.get_user_identity(current_user.id)
