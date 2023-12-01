from typing import List
from uuid import UUID

from app.models.settings import get_supabase_db
from app.models.testcase_data import TestCaseDataEntity


def get_all_testcase_data_from_a_dataset(
        dataset_id: UUID) -> List[TestCaseDataEntity]:
    """
    Get all testcases from brain testcase
    """
    supabase_db = get_supabase_db()
    response = supabase_db.get_all_testcase_data_from_a_dataset(
        dataset_id=dataset_id
    )
    return response