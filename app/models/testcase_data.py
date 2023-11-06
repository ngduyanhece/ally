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

class TestRun(BaseModel):
    run_name: str
    batch_size: int 