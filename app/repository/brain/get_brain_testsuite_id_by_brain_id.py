from uuid import UUID

from app.models.settings import get_supabase_db


def get_brain_testsuite_id_by_brain_id(brain_id: UUID):
    """
    Get brain testsuite id by brain id
    """
    supabase_db = get_supabase_db()
    response = supabase_db.get_brain_testsuite_id_by_brain_id(brain_id)
    return response
