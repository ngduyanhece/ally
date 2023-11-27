from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class RuntimeType(str, Enum):
	OpenAi = "OpenAi"
	HuggingFace = "HuggingFace"
			 
class RuntimeEntity(BaseModel):
	id: UUID
	type: RuntimeType = RuntimeType.OpenAi
	name: str = "Default Runtime"
	model: str = "gpt-3.5"
	max_tokens: int = 256
	temperature: float = 0.9
	openai_api_key: str = ""