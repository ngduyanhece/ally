from typing import List

from fastapi import HTTPException

from app.logger import get_logger
from app.models import get_supabase_db
from app.models.chat import ChatHistory
from app.models.databases.supabase.chats import CreateUserSimulatorChatHistory

logger = get_logger(__name__)

def update_user_simulator_chat_history(
	chat_history: CreateUserSimulatorChatHistory) -> ChatHistory:
	supabase_db = get_supabase_db()
	response: List[ChatHistory] = (
		supabase_db.update_user_simulator_chat_history(chat_history)).data
	if len(response) == 0:
		raise HTTPException(
			status_code=500, detail="An exception occurred while updating chat history."
		)
	return ChatHistory(response[0])