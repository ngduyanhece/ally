from typing import Tuple
from uuid import UUID

from fastapi import HTTPException

from app.logger import get_logger
from app.models.settings import get_supabase_client
from app.modules.chat.entity.chat import (Chat, ChatHistory, CreateChatHistory,
                                          CreateChatProperties,
                                          GetChatHistoryOutput, Thread)
from app.modules.chat.repository.chats import Chats

logger = get_logger(__name__)

class ChatService:
	repository: Chats

	def __init__(self):
		supabase_client = get_supabase_client()
		self.repository = Chats(supabase_client)
	
	def get_user_chats(self, user_id: UUID) -> list[Chat]:
		"""
		List all public chats
		"""
		return self.repository.get_user_chats(user_id)
	
	def create_chat(self, user_id: UUID, chat_data: CreateChatProperties) -> Chat:
			return self.repository.create_chat(user_id, chat_data)

	def get_chat_by_id(self, chat_id: str) -> Chat:
			return self.repository.get_chat_by_id(chat_id)
	
	def update_chat(self, chat_id: str, chat_data: CreateChatProperties):
			return self.repository.update_chat(chat_id, chat_data)
	
	def delete_chat(self, chat_id: str):
			return self.repository.delete_chat(chat_id)
	
	def get_enrich_chat_history(
		self, chat_id: str, n_last_history=2) -> list[GetChatHistoryOutput]:
		history: list[dict] = self.repository.get_chat_history(chat_id)[-n_last_history:]
		if history is None:
			return []
		else:
			enriched_history: list[GetChatHistoryOutput] = []
			for message in history:
				message = ChatHistory(
					chat_id=message["chat_id"],
					message_id=message["message_id"],
					user_message=message["user_message"],
					assistant=message["assistant"],
					message_time=message["message_time"],
					brain_id=message["brain_id"],
					prompt_id=message["prompt_id"],
				)
				enriched_history.append(
					GetChatHistoryOutput(
						chat_id=(UUID(message.chat_id)),
						message_id=(UUID(message.message_id)),
						user_message=message.user_message,
						assistant=message.assistant,
						message_time=message.message_time,
						brain_id=message.brain_id,
						prompt_id=message.prompt_id,
					)
				)
			return enriched_history

	def format_chat_history(self, history) -> list[Tuple[str, str]]:
		"""Format the chat history into a list of tuples"""
		template = f"""
		USER: {history.user_message}
		ASSISTANT: {history.assistant}
		"""
		return " ".join([template.format(**message) for message in history])
		
	def update_chat_history(self, chat_history: CreateChatHistory) -> ChatHistory:
		response: list[ChatHistory] = self.repository.update_chat_history(
			chat_history)
		if len(response) == 0:
			raise HTTPException(
				status_code=500, detail="An exception occurred while updating chat history."
			)
		logger.info(response)
		return ChatHistory(**response[0])

	def get_chat_history(self, chat_id: str) -> list[GetChatHistoryOutput]:
			return self.repository.get_chat_history(chat_id)
	
	def get_message_by_id(self, message_id: str) -> ChatHistory:
		return self.repository.get_message_by_id(message_id)
	
	def create_thread_for_chat(self, chat_id: str, thread_id: str) -> Thread:
		return self.repository.create_thread_for_chat(chat_id, thread_id)
	
	def get_thread_for_chat(self, chat_id: str) -> Thread:
		return self.repository.get_thread_for_chat(chat_id)
	
	
