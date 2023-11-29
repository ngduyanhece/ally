from abc import ABC, abstractmethod

from app.modules.knowledge.entity.knowledge import (CreateKnowledgeProperties,
                                                    KnowledgeEntity)


class KnowledgeInterface(ABC):
	@abstractmethod
	def insert_knowledge(self, knowledge: CreateKnowledgeProperties) -> KnowledgeEntity:
		"""
		Add a knowledge
		"""