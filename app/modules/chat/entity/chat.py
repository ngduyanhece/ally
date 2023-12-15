from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class CreateChatProperties(BaseModel):
	chat_name: str

class CreateChatHistory(BaseModel):
	id: UUID
	user_message: str
	assistant: str
	prompt_id: Optional[UUID]
	brain_id: Optional[UUID]


class Chat(BaseModel):
	id: str
	user_id: str
	creation_time: str
	chat_name: str

class Thread(BaseModel):
	id: str
	chat_id: str
	thread_id: str
	creation_time: str
	
class ChatHistory(BaseModel):
	chat_id: str
	message_id: str
	user_message: str
	assistant: str
	message_time: str
	prompt_id: Optional[UUID]
	brain_id: Optional[UUID]

class GetChatHistoryOutput(BaseModel):
	chat_id: UUID
	message_id: UUID
	user_message: str
	assistant: str
	message_time: str
	prompt_id: Optional[UUID] | None
	brain_id: Optional[UUID] | None