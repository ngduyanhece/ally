from typing import List
from uuid import UUID

from app.models import get_supabase_db
from app.models.brain_testsuite import BrainTestCaseEntity


def get_brain_testcase_by_testsuite_id(
    brain_testsuite_id: UUID,
) -> List[BrainTestCaseEntity]:
    supabase_db = get_supabase_db()
    return supabase_db.get_brain_testcase_by_testsuite_id(brain_testsuite_id)
