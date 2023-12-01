from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.brain.entity.brain import (CreateRuntimeProperties,
                                            RuntimeEntity)


class BrainsInterface(ABC):
	@abstractmethod
	def create_runtime(
		self, runtime: CreateRuntimeProperties, user_id: UUID) -> RuntimeEntity:
		"""
		Creates a runtime
		"""