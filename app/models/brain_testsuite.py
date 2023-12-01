

from uuid import UUID

from pydantic import BaseModel


class BrainTestSuiteEntity(BaseModel):
    brain_testsuite_id: UUID
    brain_id: UUID
    name: str
    scoring_method: str
    last_update: str

    @property
    def id(self) -> UUID:
        return self.brain_id

    def dict(self, **kwargs):
        data = super().model_dump(
            **kwargs,
        )
        data["id"] = self.id
        return data


class BrainTestCaseEntity(BaseModel):
    brain_testcase_id: UUID
    brain_testsuite_id: UUID
    description: str
    last_update: str

    
