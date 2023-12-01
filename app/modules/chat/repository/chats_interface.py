from abc import ABC, abstractmethod


class ChatsInterface(ABC):
	@abstractmethod
	def create_chat(self, new_chat):
		"""
		Create a chat
		"""
		pass

	