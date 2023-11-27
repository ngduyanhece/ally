from pydantic import BaseModel


class ApiKeyInfo(BaseModel):
	id: str
	creation_time: str

class ApiKey(BaseModel):
	api_key: str
	id: str