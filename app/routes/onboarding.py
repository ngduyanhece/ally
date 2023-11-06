from fastapi import APIRouter, Depends, status

from app.auth.auth_bearer import AuthBearer, get_current_user
from app.models.databases.supabase.onboarding import (
    OnboardingStates, OnboardingUpdatableProperties)
from app.models.user_identity import UserIdentity
from app.repository.onboarding.get_user_onboarding import get_user_onboarding
from app.repository.onboarding.update_user_onboarding import \
    update_user_onboarding

router = APIRouter()

@router.get(
        "/onboarding",
        status_code=status.HTTP_200_OK,
        dependencies=[Depends(AuthBearer())],
)
async def get_user_onboarding_handler(
    current_user: UserIdentity = Depends(get_current_user),
) -> OnboardingStates | None:
    """
    Get user onboarding information for the current user
    """
    return get_user_onboarding(current_user.id)


@router.put(
    "/onboarding",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(AuthBearer())],
)
async def update_user_onboarding_handler(
    onboarding: OnboardingUpdatableProperties,
    current_user: UserIdentity = Depends(get_current_user),
) -> OnboardingStates:
    """
    Update user onboarding information for the current user
    """

    return update_user_onboarding(current_user.id, onboarding)