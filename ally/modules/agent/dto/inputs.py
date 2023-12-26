from enum import Enum
from typing import Optional

from pydantic import BaseModel


class ModelTye(str, Enum):
	gpt_3_turbo = "gpt-3.5-turbo-1106"
	gpt_4_turbo = "gpt-4-1106-preview"

class CreateAgentProperties(BaseModel):
	"""The properties to create an agent."""
	name: str
	instructions: str
	model: Optional[ModelTye]

class AgentUpdatableProperties(BaseModel):
	"""The properties to update an agent."""
	name: Optional[str]
	instructions: Optional[str]
	model: Optional[ModelTye]
