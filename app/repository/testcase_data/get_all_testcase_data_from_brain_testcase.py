from uuid import UUID

from app.models.settings import get_supabase_db


def get_all_testcase_data_from_brain_testcase(brain_testcase_id: UUID):
    """
    Get all testcases from brain testcase
    """
    supabase_db = get_supabase_db()
    response = supabase_db.get_all_testcase_data_from_brain_testcase(
        brain_testcase_id=brain_testcase_id
    )
    return response