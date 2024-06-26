from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.logger import get_logger
from app.models.chats import MessageLabel, MessageLabelOutput
from app.models.databases.repository import Repository

logger = get_logger(__name__)
class CreateChatHistory(BaseModel):
    chat_id: UUID
    user_message: str
    assistant: str
    prompt_id: Optional[UUID]
    brain_id: Optional[UUID]

class CreateUserSimulatorChatHistory(BaseModel):
    chat_id: UUID
    user_message: str
    assistant: str
    task_goal: str
    brain_id: Optional[UUID]
    context: Optional[str]

class Chats(Repository):
    def __init__(self, supabase_client):
        self.db = supabase_client

    def create_chat(self, new_chat):
        response = self.db.table("chats").insert(new_chat).execute()
        return response

    def get_chat_by_id(self, chat_id: str):
        response = (
            self.db.from_("chats")
            .select("*")
            .filter("chat_id", "eq", chat_id)
            .execute()
        )
        return response

    def get_chat_history(self, chat_id: str):
        response = (
            self.db.from_("chat_history")
            .select("*")
            .filter("chat_id", "eq", chat_id)
            .order("message_time", desc=False)  # Add the ORDER BY clause
            .execute()
        )

        return response

    def get_user_chats(self, user_id: str):
        response = (
            self.db.from_("chats")
            .select("chat_id,user_id,creation_time,chat_name")
            .filter("user_id", "eq", user_id)
            .order("creation_time", desc=False)
            .execute()
        )
        return response

    def update_chat_history(self, chat_history: CreateChatHistory):
        response = (
            self.db.table("chat_history")
            .insert(
                {
                    "chat_id": str(chat_history.chat_id),
                    "user_message": chat_history.user_message,
                    "assistant": chat_history.assistant,
                    "prompt_id": str(chat_history.prompt_id)
                    if chat_history.prompt_id
                    else None,
                    "brain_id": str(chat_history.brain_id)
                    if chat_history.brain_id
                    else None,
                }
            )
            .execute()
        )

        return response
    
    def update_user_simulator_chat_history(self, chat_history: CreateUserSimulatorChatHistory):
        response = (
            self.db.table("user_simulator_chat_history")
            .insert(
                {
                    "chat_id": str(chat_history.chat_id),
                    "user_message": chat_history.user_message,
                    "assistant": chat_history.assistant,
                    "task_goal": chat_history.task_goal,
                    "brain_id": str(chat_history.brain_id),
                    "context": chat_history.context,
                }
            )
            .execute()
        )
        return response

    def update_chat(self, chat_id, updates):
        response = (
            self.db.table("chats").update(updates).match({"chat_id": chat_id}).execute()
        )

        return response

    def update_message_by_id(self, message_id, updates):
        response = (
            self.db.table("chat_history")
            .update(updates)
            .match({"message_id": message_id})
            .execute()
        )

        return response

    def get_chat_details(self, chat_id):
        response = (
            self.db.from_("chats")
            .select("*")
            .filter("chat_id", "eq", chat_id)
            .execute()
        )
        return response

    def delete_chat(self, chat_id):
        self.db.table("chats").delete().match({"chat_id": chat_id}).execute()

    def delete_chat_history(self, chat_id):
        self.db.table("chat_history").delete().match({"chat_id": chat_id}).execute()
    
    def create_message_label_by_id(
        self, message_label: MessageLabel, message_id, user_id
    ) -> MessageLabel:
        response = (
            self.db.from_("label")
            .insert(
                {
                    "message_id": str(message_id),
                    "user_id": str(user_id),
                    "label": message_label.label,
                    "feedback": message_label.feedback,
                }
            )
            .execute()
        )

        return MessageLabel(**response.data[0])
    
    def update_message_label_by_id(
        self, message_label: MessageLabel, message_id, user_id
    ) -> MessageLabel:
        response = (
            self.db.from_("label")
            .update(
                {
                    "label": message_label.label,
                    "feedback": message_label.feedback,
                }
            )
            .filter("message_id", "eq", message_id)
            .filter("user_id", "eq", user_id)
            .execute()
        )

        return MessageLabel(**response.data[0])
    
    def delete_message_label_by_id(
        self, message_id, user_id
    ):
        response = (
            self.db.from_("label")
            .delete()
            .filter("message_id", "eq", message_id)
            .filter("user_id", "eq", user_id)
            .execute()
        )

        return response.data[0]
    
    def get_message_label_by_id(self, message_id: UUID) -> MessageLabelOutput | None:
        response = (
            self.db.from_("label")
            .select("*")
            .filter("message_id", "eq", message_id)
            .execute()
        ).data
        if len(response) == 0:
            return None
        return MessageLabelOutput(**response[0])
    
