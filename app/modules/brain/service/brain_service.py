from uuid import UUID

from app.logger import get_logger
from app.models.settings import get_supabase_client
from app.modules.brain.entity.brain import (BrainEntity,
                                            CreateFullBrainProperties,
                                            CreateRuntimeProperties,
                                            FullBrainEntity,
                                            FullBrainEntityWithRights,
                                            MinimalBrainEntity, RoleEnum,
                                            RuntimeEntity,
                                            UpdateBrainProperties)
from app.modules.brain.repository.brains import Brains

logger = get_logger(__name__)

class BrainService:
	repository: Brains

	def __init__(self):
		supabase_client = get_supabase_client()
		self.repository = Brains(supabase_client)
	
	def get_user_brains(self, user_id: UUID) -> list[FullBrainEntityWithRights]:
		return self.repository.get_user_brains(user_id)
	
	def create_runtime(
			self, runtime: CreateRuntimeProperties, user_id: UUID) -> RuntimeEntity:
		return self.repository.create_runtime(runtime, user_id)
	
	def create_brain(self, brain: CreateFullBrainProperties) -> FullBrainEntity:
		return self.repository.create_brain(brain)
	
	def get_user_default_brain(self, user_id: UUID) -> FullBrainEntityWithRights | None:
			
		brain_id = self.repository.get_default_user_brain_id(user_id)

		logger.info(f"Default brain response: {brain_id}")

		if brain_id is None:
			return None

		logger.info(f"Default brain id: {brain_id}")

		return self.repository.get_brain_by_id(brain_id)
	
	def create_brain_user(
		self, user_id: UUID, brain_id, rights, is_default_brain: bool):
		return self.repository.create_brain_user(
			user_id, brain_id, rights, is_default_brain)
	
	def get_default_user_brain_or_create_new(
		self, user_id: UUID) -> FullBrainEntityWithRights:
			
		default_brain = self.get_user_default_brain(user_id)

		if not default_brain:
			brain = self.create_brain(CreateFullBrainProperties())
			response = self.create_brain_user(
				user_id, default_brain.brain_id, RoleEnum.Owner, True)
			default_brain = FullBrainEntityWithRights(
				id=brain.id,
				name=brain.name,
				description=brain.description,
				status=brain.status,
				prompt_id=brain.prompt_id,
				runtime=brain.runtime,
				teacher_runtime=brain.teacher_runtime,
				last_update=brain.last_update,
				rights=RoleEnum.Owner,
			)
			
		return default_brain
	
	def get_brain_details(self, brain_id: UUID) -> FullBrainEntityWithRights:
		return self.repository.get_brain_by_id(brain_id)

	def get_brain_for_user(
		self, user_id: UUID, brain_id: UUID) -> MinimalBrainEntity:
		return self.repository.get_brain_for_user(user_id, brain_id)
	
	def update_brain_by_id(self, brain_id: UUID, brain: UpdateBrainProperties):
		return self.repository.update_brain_by_id(brain_id, brain)
	
	def delete_brain_by_id(self, brain_id: UUID) -> BrainEntity:
			return self.repository.delete_brain_by_id(brain_id)
	
	def update_runtime_by_id(
		self, runtime_id: str, runtime: CreateRuntimeProperties) -> RuntimeEntity:
		return self.repository.update_runtime_by_id(runtime_id, runtime)
	
	def set_as_default_brain_for_user(self, user_id: UUID, brain_id: UUID):
		return self.repository.set_as_default_brain_for_user(user_id, brain_id)
		

	