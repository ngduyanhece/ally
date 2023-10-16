from uuid import UUID

from app.models.settings import get_supabase_db


def delete_meta_brain_user(user_id: UUID, meta_brain_id: UUID) -> None:
    supabase_db = get_supabase_db()
    supabase_db.delete_meta_brain_user_by_id(
        user_id=user_id,
        meta_brain_id=meta_brain_id,
    )
