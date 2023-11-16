from uuid import UUID

from pydantic import BaseModel


class TestCaseDataDescription(BaseModel):
	description: str

class TestCaseDataEntity(BaseModel):
	testcase_data_id: UUID
	description: str
	input: str
	reference_output: str
	context: str
	last_update: str

	def dict(self, *args, **kwargs):
		test_case_dict = super().model_dump(*args, **kwargs)
		return test_case_dict

class TestRun(BaseModel):
	run_name: str
	batch_size: int 