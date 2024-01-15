from pydantic import BaseModel


class UserSignInProperties(BaseModel):
	email: str
	password: str

class UserUpdatableProperties(BaseModel):
    # Nothing for now
    empty: bool = True
