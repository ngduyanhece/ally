from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class UserSignInProperties(BaseModel):
	email: str
	password: str

class UserIdentity(BaseModel):
	id: UUID
	email: Optional[str] = None
	openai_api_key: Optional[str] = None