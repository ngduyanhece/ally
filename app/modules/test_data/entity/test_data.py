from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class MessageLabel(BaseModel):
	label: Optional[str]
	feedback: Optional[str]

class MessageLabelOutput(BaseModel):
	id: Optional[str]
	user_id: Optional[str]
	label: Optional[str]
	feedback: Optional[str]

class TestCaseDataDescription(BaseModel):
	description: str

class TestCaseDataEntity(BaseModel):
	testcase_data_id: UUID
	description: str
	text_input: str
	reference_output: str
	context: str
	last_update: str
	
	def dict(self, *args, **kwargs):
		test_case_dict = super().model_dump(*args, **kwargs)
		return test_case_dict

class TestRun(BaseModel):
	run_name: str
	batch_size: int