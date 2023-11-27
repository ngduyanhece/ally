from uuid import UUID

from pydantic import BaseModel


class DatasetEntity(BaseModel):
		id: UUID
		name: str
		description: str