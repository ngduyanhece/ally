from app.models import get_supabase_db
from app.models.brain_testsuite import BrainTestSuiteEntity


def delete_brain_testsuite_by_id(
    brain_id: str,
) -> BrainTestSuiteEntity:
    supabase_db = get_supabase_db()

    return supabase_db.delete_brain_testsuite_by_id(brain_id)
