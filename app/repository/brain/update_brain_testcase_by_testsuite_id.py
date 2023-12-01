from uuid import UUID

from app.models import get_supabase_db
from app.models.brain_testsuite import BrainTestSuiteEntity
from app.models.databases.supabase.brains import UpdateBrainTestcaseProperties


def update_brain_testcase_by_test_suite_id(
    brain_testsuite_id: UUID,
    brain_testcase_id: UUID,
    brain_testcase: UpdateBrainTestcaseProperties
) -> BrainTestSuiteEntity:
    supabase_db = get_supabase_db()
    return supabase_db.update_brain_testcase_by_test_suite_id(
        brain_testsuite_id, brain_testcase_id, brain_testcase)
