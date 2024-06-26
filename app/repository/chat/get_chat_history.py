from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from app.models.chat import ChatHistory
from app.models.settings import get_supabase_db
from app.repository.brain import get_brain_by_id
from app.repository.prompt import get_prompt_by_id


class GetChatHistoryOutput(BaseModel):
    chat_id: UUID
    message_id: UUID
    user_message: str
    assistant: str
    message_time: str
    prompt_id: Optional[str] | None
    brain_id: Optional[str] | None

    def dict(self, *args, **kwargs):
        chat_history = super().model_dump(*args, **kwargs)
        chat_history["chat_id"] = str(chat_history.get("chat_id"))
        chat_history["message_id"] = str(chat_history.get("message_id"))

        return chat_history


def get_chat_history(chat_id: str, n_last_history=1) -> List[GetChatHistoryOutput]:
    supabase_db = get_supabase_db()
    history: List[dict] = supabase_db.get_chat_history(chat_id).data[-n_last_history:]
    if history is None:
        return []
    else:
        enriched_history: List[GetChatHistoryOutput] = []
        for message in history:
            message = ChatHistory(message)
            brain = None
            if message.brain_id:
                brain = get_brain_by_id(message.brain_id)

            prompt = None
            if message.prompt_id:
                prompt = get_prompt_by_id(message.prompt_id)

            enriched_history.append(
                GetChatHistoryOutput(
                    chat_id=(UUID(message.chat_id)),
                    message_id=(UUID(message.message_id)),
                    user_message=message.user_message,
                    assistant=message.assistant,
                    message_time=message.message_time,
                    brain_id=str(brain.id) if brain else None,
                    prompt_id=str(prompt.id) if prompt else None,
                )
            )
        return enriched_history
