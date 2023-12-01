from app.models import BrainEntity, UserIdentity
from app.models.databases.supabase.brains import CreateBrainProperties
from app.repository.brain import (create_brain, create_brain_user,
                                  get_user_default_brain)
from app.routes.authorizations.types import RoleEnum


def get_default_user_brain_or_create_new(user: UserIdentity) -> BrainEntity:
    default_brain = get_user_default_brain(user.id)

    if not default_brain:
        default_brain = create_brain(CreateBrainProperties())
        create_brain_user(user.id, default_brain.brain_id, RoleEnum.Owner, True)

    return default_brain
