import uuid

from app.models.settings import get_supabase_db


def create_brain_testrun_for_brain_testcase_id(
    brain_testcase_id: uuid,
    average_score: float = 0.0,
):
    """
    Create a brain testrun for a brain testcase
    """
    supabase_db = get_supabase_db()
    response = supabase_db.create_brain_testrun_for_brain_testcase_id(
        brain_testcase_id=brain_testcase_id,
        average_score=average_score,
    )
    return response