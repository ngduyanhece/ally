from pydantic import BaseModel


class ApiKey(BaseModel):
	id: str
	user_id: str
	api_key: str
	email: str
	creation_time: str
	is_active: bool
