from typing import List
from uuid import UUID

from app.modules.brain.entity.brain import (BrainEntity, BrainToolEntity,
                                            BrainToolkitEntity,
                                            CreateFullBrainProperties,
                                            CreateRuntimeProperties,
                                            FullBrainEntityWithRights,
                                            MinimalBrainEntity, RuntimeEntity,
                                            RuntimeType, UpdateBrainProperties)
from app.modules.brain.repository.brains_interface import BrainsInterface


class Brains(BrainsInterface):
	def __init__(self, supabase_client):
		self.db = supabase_client
	
	def create_runtime(
		self, runtime: CreateRuntimeProperties, user_id: UUID) -> RuntimeEntity:
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
			.filter("id", "eq", runtime_id)
			.execute()
		).data
		if len(response) == 0:
			raise ValueError("Runtime not found")
		return RuntimeEntity(**response[0])
	
	def create_brain(self, brain: CreateFullBrainProperties) -> BrainEntity:
		response = (
			self.db.table("brains").insert({
				"name": brain.name,
				"description": brain.description,
				"status": brain.status,
				"prompt_id": str(brain.prompt_id) if brain.prompt_id else None,
				"runtime_id": str(brain.runtime_id) if brain.runtime_id else None,
				"teacher_runtime_id": str(brain.teacher_runtime_id) if brain.teacher_runtime_id else None,
			}).execute()
		).data[0]
		return BrainEntity(**response)
	
	def get_user_brains(self, user_id) -> list[FullBrainEntityWithRights]:
		response = (
			self.db.from_("brains_users")
			.select("id:brain_id, rights, brains (id, name, description, prompt_id, status, last_update, runtime_id, teacher_runtime_id)")
			.filter("user_id", "eq", user_id)
			.execute()
		)
		user_brains: list[FullBrainEntityWithRights] = []
		for item in response.data:
			runtime = self.get_runtime_by_id(item["brains"]["runtime_id"])
			teacher_runtime = self.get_runtime_by_id(item["brains"]["teacher_runtime_id"])
			user_brains.append(
				FullBrainEntityWithRights(
					id=item["brains"]["id"],
					name=item["brains"]["name"],
					description=item["brains"]["description"],
					status=item["brains"]["status"],
					prompt_id=item["brains"]["prompt_id"],
					runtime=runtime,
					teacher_runtime=teacher_runtime,
					last_update=item["brains"]["last_update"],
					rights=item["rights"],
				)
			)
			user_brains[-1].rights = item["rights"]
		return user_brains
	
	def get_default_user_brain_id(self, user_id: UUID) -> UUID | None:
		response = (
			(
				self.db.from_("brains_users")
				.select("brain_id")
				.filter("user_id", "eq", user_id)
				.filter("default_brain", "eq", True)
				.execute()
			)
		).data
		if len(response) == 0:
			return None
		return UUID(response[0].get("brain_id"))
	
	def get_brain_by_id(self, brain_id: UUID) -> FullBrainEntityWithRights | None:
		brain_response = (
			self.db.from_("brains")
			.select("id, name, *")
			.filter("id", "eq", brain_id)
			.execute()
		).data

		if len(brain_response) == 0:
			return None
		runtime = self.get_runtime_by_id(brain_response[0]["runtime_id"])
		teacher_runtime = self.get_runtime_by_id(brain_response[0]["teacher_runtime_id"])
		brain_user_response = (
			self.db.from_("brains_users")
			.select("rights")
			.filter("brain_id", "eq", brain_id)
			.execute()
		).data
		brain = FullBrainEntityWithRights(
			id=brain_response[0]["id"],
			name=brain_response[0]["name"],
			description=brain_response[0]["description"],
			status=brain_response[0]["status"],
			prompt_id=brain_response[0]["prompt_id"],
			runtime=runtime,
			teacher_runtime=teacher_runtime,
			last_update=brain_response[0]["last_update"],
			rights=brain_user_response[0]["rights"],
		)
		return brain
	
	def create_brain_user(self, user_id: UUID, brain_id, rights, default_brain: bool):
		response = (
			self.db.table("brains_users")
			.insert(
				{
					"brain_id": str(brain_id),
					"user_id": str(user_id),
					"rights": rights,
					"default_brain": default_brain,
				}
			)
			.execute()
		)

		return response
	
	def get_brain_for_user(self, user_id, brain_id) -> MinimalBrainEntity | None:
		response = (
			self.db.from_("brains_users")
			.select("id:brain_id, rights, brains (id, status, name)")
			.filter("user_id", "eq", user_id)
			.filter("brain_id", "eq", brain_id)
			.execute()
		)
		if len(response.data) == 0:
			return None
		brain_data = response.data[0]

		return MinimalBrainEntity(
			id=brain_data["brains"]["id"],
			name=brain_data["brains"]["name"],
			rights=brain_data["rights"],
			status=brain_data["brains"]["status"],
		)
	
	def update_brain_by_id(
		self, brain_id: UUID, brain: UpdateBrainProperties
	) -> BrainEntity | None:
		update_brain_response = (
			self.db.table("brains")
			.update({
				"name": brain.name,
				"description": brain.description,
				"status": brain.status,
				"prompt_id": str(brain.prompt_id) if brain.prompt_id else None,
			})
			.match({"id": brain_id})
			.execute()
		).data

		if len(update_brain_response) == 0:
			return None

		return BrainEntity(**update_brain_response[0])
	
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
	
	def delete_brain_user_by_id(
		self,
		user_id: UUID,
		brain_id: UUID,
	):
		results = (
			self.db.table("brains_users")
			.delete()
			.match({"brain_id": str(brain_id), "user_id": str(user_id)})
			.execute()
		)
		return results.data
	
	def delete_brain_by_id(self, brain_id: UUID):
		_ = (
			self.db.table("brains_users")
			.delete()
			.match({"brain_id": str(brain_id)})
			.execute()
		)
		brain_results = (
			self.db.table("brains")
			.delete()
			.match({"id": str(brain_id)})
			.execute()
		)
		runtime_id = brain_results.data[0]["runtime_id"]
		teacher_runtime_id = brain_results.data[0]["teacher_runtime_id"]
		_ = (
			self.db.table("runtimes")
			.delete()
			.match({"id": str(runtime_id)})
			.execute()
		)
		_ = (
			self.db.table("runtimes")
			.delete()
			.match({"id": str(teacher_runtime_id)})
			.execute()
		)
		return brain_results.data[0]
	
	def set_as_default_brain_for_user(self, user_id: UUID, brain_id: UUID):

		old_default_brain = self.get_default_user_brain_id(user_id)

		if old_default_brain is not None:
			self.db.table("brains_users").update({"default_brain": False}).match(
				{"brain_id": old_default_brain, "user_id": user_id}
			).execute()

		self.db.table("brains_users").update({"default_brain": True}).match(
			{"brain_id": brain_id, "user_id": user_id}
		).execute()
	
	def update_brain_last_update_time(self, brain_id: UUID) -> None:
		self.db.table("brains").update({"last_update": "now()"}).match(
			{"id": brain_id}
		).execute()
	
	def create_brain_vector(self, brain_id, vector_id, file_sha1):
		response = (
			self.db.table("brains_vectors")
			.insert(
				{
					"brain_id": str(brain_id),
					"vector_id": str(vector_id),
					"file_sha1": file_sha1,
				}
			)
			.execute()
		)
		return response.data
	
	def delete_file_from_brain(self, brain_id, file_name: str):
		# First, get the vector_ids associated with the file_name
		file_vectors = (
			self.db.table("vectors")
			.select("id")
			.filter("metadata->>file_name", "eq", file_name)
			.execute()
		)

		file_vectors_ids = [item["id"] for item in file_vectors.data]

		# remove current file vectors from brain vectors
		self.db.table("brains_vectors").delete().in_("vector_id", file_vectors_ids).filter("brain_id", "eq", brain_id).execute()

		vectors_used_by_another_brain = (
			self.db.table("brains_vectors")
			.select("vector_id")
			.in_("vector_id", file_vectors_ids)
			.filter("brain_id", "neq", brain_id)
			.execute()
		)
		vectors_used_by_another_brain_ids = [
			item["vector_id"] for item in vectors_used_by_another_brain.data
		]

		vectors_no_longer_used_ids = [
			id for id in file_vectors_ids if id not in vectors_used_by_another_brain_ids
		]

		self.db.table("vectors").delete().in_("id", vectors_no_longer_used_ids).execute()

		return {"message": f"File {file_name} in brain {brain_id} has been deleted."}
	
	def get_tools_from_brain(self, brain_id: UUID) -> List[BrainToolEntity]:
		response = (
			self.db.from_("tools")
			.select("id, name, tool_kwargs")
			.filter("brain_id", "eq", brain_id)
			.execute()
		)
		tools: List[BrainToolEntity] = []
		for item in response.data:
				tools.append(
					BrainToolEntity(
						id=item["id"],
						name=item["name"],
						tool_kwargs=item["tool_kwargs"],
					)
				)
		return tools
	
	def get_toolkits_from_brain(self, brain_id: UUID) -> List[BrainToolkitEntity]:
		response = (
			self.db.from_("toolkits")
			.select("id, name")
			.filter("brain_id", "eq", brain_id)
			.execute()
		)
		toolkits: List[BrainToolkitEntity] = []
		for item in response.data:
				toolkits.append(
					BrainToolkitEntity(
						id=item["id"],
						name=item["name"],
					)
				)
		return toolkits
	
	def create_assistant_for_brain(self, brain_id: UUID, assistant_id: str):
		response = (
			self.db.from_("brains_assistants")
			.insert(
				{
					"brain_id": str(brain_id),
					"assistant_id": assistant_id,
				}
			).execute()
		)
	
	def get_assistant_form_brain(self, brain_id: UUID) -> str | None:
		response = (
			self.db.from_("brains_assistants")
			.select("assistant_id")
			.filter("brain_id", "eq", brain_id)
			.execute()
		)
		if len(response.data) == 0:
			return None
		return response.data[0]["assistant_id"]

	

	

			
