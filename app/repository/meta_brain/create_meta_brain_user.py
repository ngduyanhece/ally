from uuid import UUID

from app.models.settings import get_supabase_db
from app.routes.authorizations.types import RoleEnum


def create_meta_brain_user(
    user_id: UUID, meta_brain_id: UUID, rights: RoleEnum, is_default_meta_brain: bool
) -> None:
    supabase_db = get_supabase_db()
    supabase_db.create_meta_brain_user(
        user_id=user_id,
        meta_brain_id=meta_brain_id,
        rights=rights,
        default_meta_brain=is_default_meta_brain,
    ).data[0]
