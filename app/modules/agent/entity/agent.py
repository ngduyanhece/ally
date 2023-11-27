from pydantic import BaseModel


class BrainAgentInput(BaseModel):
	text_input: str
