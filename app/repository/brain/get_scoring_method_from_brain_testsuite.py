from uuid import UUID

from app.models import get_supabase_db
from app.models.brain_testsuite import BrainTestSuiteEntity


def get_scoring_method_from_brain_testsuite(
    brain_testsuite_id: UUID,
) -> BrainTestSuiteEntity:
    supabase_db = get_supabase_db()
    return supabase_db.get_scoring_method_from_brain_testsuite(
        brain_testsuite_id)
