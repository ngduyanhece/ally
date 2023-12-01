from uuid import UUID

from app.models.settings import get_supabase_db


def update_meta_brain_last_update_time(meta_brain_id: UUID):
    supabase_db = get_supabase_db()
    supabase_db.update_brain_last_update_time(meta_brain_id)
