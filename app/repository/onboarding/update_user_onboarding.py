from uuid import UUID

from app.models.databases.supabase.onboarding import (
    OnboardingStates, OnboardingUpdatableProperties)
from app.models.settings import get_supabase_db


def update_user_onboarding(
    user_id: UUID, onboarding: OnboardingUpdatableProperties
) -> OnboardingStates:
    """Update user onboarding information by user_id"""

    supabase_db = get_supabase_db()
    updated_onboarding = supabase_db.update_user_onboarding(user_id, onboarding)

    if all(not value for value in updated_onboarding.model_dump().values()):
        supabase_db.remove_user_onboarding(user_id)

    return updated_onboarding
