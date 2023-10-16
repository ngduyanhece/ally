from uuid import UUID

from app.models import get_supabase_db


def create_brain_meta_brain(
    brain_id: UUID, meta_brain_id: UUID
) -> None:
    supabase_db = get_supabase_db()
    supabase_db.create_brain_meta_brain(
        brain_id=brain_id,
        meta_brain_id=meta_brain_id
    ).data[0]
