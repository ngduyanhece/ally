from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.models.databases.repository import Repository
from app.models.runtimes import RuntimeEntity, RuntimeType


class CreateRuntimeProperties(BaseModel):
	"""Properties that can be received on runtime creation"""
	type: RuntimeType
	name: str
	model: str
	max_tokens: int
	temperature: float
	openai_api_key: Optional[str] = None
		
class Runtime(Repository):
		def __init__(self, supabase_client):
			self.db = supabase_client

		def get_user_runtimes(self, user_id: UUID) -> list[RuntimeEntity]:
			"""
			Returns all runtimes of a user
			"""
			response = (
				self.db.from_("runtimes")
				.select("*")
				.filter("user_id", "eq", str(user_id))
				.execute()
			).data
			runtimes: list[RuntimeEntity] = []
			for runtime in response:
					runtimes.append(RuntimeEntity(
						id=runtime["id"],
						type=runtime["type"],
						name=runtime["name"],
						model=runtime["model"],
						max_tokens=runtime["max_tokens"],
						temperature=runtime["temperature"],
						openai_api_key=str(runtime["openai_api_key"]),
					))
			return runtimes
		
		def create_runtime(self, runtime: CreateRuntimeProperties, user_id: UUID) -> RuntimeEntity:
			"""
			Creates a runtime
			"""
			if runtime.type == RuntimeType.OpenAi:
				if runtime.openai_api_key is None:
					raise ValueError("OpenAI API key is required for OpenAI runtimes")
				response = (
					self.db.from_("runtimes")
					.insert(
						{
							"user_id": str(user_id),
							"name": runtime.name,
							"model": runtime.model,
							"max_tokens": runtime.max_tokens,
							"temperature": runtime.temperature,
							"openai_api_key": runtime.openai_api_key,
							"type": runtime.type,
						}
					)
					.execute()
				).data
			elif runtime.type == RuntimeType.HuggingFace:
				if runtime.openai_api_key:
					raise ValueError("OpenAI API key is not required for HuggingFace runtimes")
				response = (
					self.db.from_("runtimes")
					.insert(
						{
							"user_id": str(user_id),
							"name": runtime.name,
							"model": runtime.model,
							"max_tokens": runtime.max_tokens,
							"temperature": runtime.temperature,
							"openai_api_key": "",
							"type": runtime.type,
						}
					)
					.execute()
				).data
			else:
				raise NotImplementedError(f'Runtime type {runtime.type} is not implemented.')
			return RuntimeEntity(**response[0])
		
		def get_runtime_by_id(self, runtime_id: UUID) -> RuntimeEntity:
			"""
			Returns a runtime by its id
			"""
			response = (
				self.db.from_("runtimes")
				.select("*")
				.filter("id", "eq", str(runtime_id))
				.execute()
			).data
			if len(response) == 0:
				raise ValueError("Runtime not found")
			return RuntimeEntity(**response[0])
	
		def update_runtime_by_id(
				self, runtime_id: UUID, runtime: CreateRuntimeProperties) -> RuntimeEntity:
			"""
			Updates a runtime by its id
			"""
			if runtime.type == RuntimeType.OpenAi:
				if runtime.openai_api_key is None:
					raise ValueError("OpenAI API key is required for OpenAI runtimes")
				response = (
					self.db.from_("runtimes")
					.update(
						{
							"name": runtime.name,
							"model": runtime.model,
							"max_tokens": runtime.max_tokens,
							"temperature": runtime.temperature,
							"openai_api_key": runtime.openai_api_key,
							"type": runtime.type,
						}
					)
					.filter("id", "eq", str(runtime_id))
					.execute()
				).data
			elif runtime.type == RuntimeType.HuggingFace:
				if runtime.openai_api_key:
					raise ValueError("OpenAI API key is not required for HuggingFace runtimes")
				response = (
					self.db.from_("runtimes")
					.update(
						{
							"name": runtime.name,
							"model": runtime.model,
							"max_tokens": runtime.max_tokens,
							"temperature": runtime.temperature,
							"openai_api_key": "",
							"type": runtime.type,
						}
					)
					.filter("id", "eq", str(runtime_id))
					.execute()
				).data
			else:
				raise NotImplementedError(f'Runtime type {runtime.type} is not implemented.')
			if len(response) == 0:
					raise ValueError("Runtime not found")
			
			return RuntimeEntity(**response[0])
	
		def delete_runtime_by_id(self, runtime_id: UUID) -> RuntimeEntity:
			"""
			Deletes a runtime by its id
			"""
			response = (
				self.db.from_("runtimes")
				.delete()
				.filter("id", "eq", str(runtime_id))
				.execute()
			).data
			if len(response) == 0:
				raise ValueError("Runtime not found")
			return RuntimeEntity(**response[0])
