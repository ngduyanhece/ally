from app.logger import get_logger
from app.models.settings import get_supabase_db
from app.models.testcase_data import TestCaseDataEntity

logger = get_logger(__name__)


def delete_testcase_data_by_id(
    testcase_data_id: str
) -> TestCaseDataEntity:
    supabase_db = get_supabase_db()
    response = supabase_db.delete_testcase_data_by_id(testcase_data_id)
    if len(response.data) == 0:
        return None
    return TestCaseDataEntity(**response.data[0])