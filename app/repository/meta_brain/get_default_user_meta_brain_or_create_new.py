from app.models.databases.supabase.meta_brains import CreateMetaBrainProperties
from app.models.meta_brain_entity import MetaBrainEntity
from app.modules.user.entity.user_identity import UserIdentity
from app.repository.meta_brain.create_meta_brain import create_meta_brain
from app.repository.meta_brain.create_meta_brain_user import \
    create_meta_brain_user
from app.repository.meta_brain.get_default_user_meta_brain import \
    get_user_default_meta_brain
from app.routes.authorizations.types import RoleEnum


def get_default_user_brain_or_create_new(user: UserIdentity) -> MetaBrainEntity:
    default_meta_brain = get_user_default_meta_brain(user.id)

    if not default_meta_brain:
        default_meta_brain = create_meta_brain(CreateMetaBrainProperties())
        create_meta_brain_user(user.id, default_meta_brain.meta_brain_id, RoleEnum.Owner, True)

    return default_meta_brain
