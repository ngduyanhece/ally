from uuid import UUID

from app.models.settings import get_supabase_db
from app.models.testcase_data import TestCaseDataEntity


def get_testcase_data_by_id(testcase_data_id: UUID) -> TestCaseDataEntity:
	"""
	Get all testcases from brain testcase
	"""
	supabase_db = get_supabase_db()
	response = supabase_db.get_testcase_data_by_id(
		testcase_data_id=testcase_data_id
	)
	return response