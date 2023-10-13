from typing import List

from app.models.chat import Chat
from app.models.settings import get_supabase_db


def get_user_chats(user_id: str) -> List[Chat]:
    supabase_db = get_supabase_db()
    response = supabase_db.get_user_chats(user_id)
    chats = [Chat(chat_dict) for chat_dict in response.data]
    return chats
