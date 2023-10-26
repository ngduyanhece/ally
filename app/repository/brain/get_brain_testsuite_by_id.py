from uuid import UUID

from app.models import get_supabase_db
from app.models.brain_testsuite import BrainTestSuiteEntity


def get_brain_testsuite_by_id(
    brain_id: UUID,
) -> BrainTestSuiteEntity:
    supabase_db = get_supabase_db()

    return supabase_db.get_brain_testsuite_by_id(brain_id)
