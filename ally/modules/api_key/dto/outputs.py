from pydantic import BaseModel


class ApiKeyInfo(BaseModel):
	id: str
	creation_time: str
