

from uuid import UUID

from app.models.settings import get_supabase_db


def add_testcase_data_to_brain_testcase(
    testcase_data_id: UUID,
    brain_testcase_id: UUID,
):
    """
    Add testcase data to brain testcase
    """
    supabase_db = get_supabase_db()
    response = supabase_db.add_testcase_data_to_brain_testcase(
        brain_testcase_id=brain_testcase_id,
        testcase_data_id=testcase_data_id,
    )
    return response