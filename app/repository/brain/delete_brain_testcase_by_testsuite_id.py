from uuid import UUID

from app.models import get_supabase_db


def delete_brain_testcase_by_test_suite_id(
    brain_testsuite_id: UUID,
    brain_testcase_id: UUID,
):
    supabase_db = get_supabase_db()
    return supabase_db.delete_brain_testcase_by_test_suite_id(
        brain_testsuite_id, brain_testcase_id)
