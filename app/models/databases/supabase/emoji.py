import enum
from uuid import UUID

from pydantic import BaseModel

from app.logger import get_logger
from app.models.databases.repository import Repository
from app.models.message_emoji import MessageEmoji

logger = get_logger(__name__)

class EmojiCode(str, enum.Enum):
    thumbs_up = "+1"  # 👍
    thumbs_down = "-1"  # 👎
    red_flag = "red_flag"  # 🚩
    hundred = "100"  # 💯
    rofl = "rofl"  # 🤣
    clap = "clap"  # 👏
    diamond = "diamond"  # 💎
    heart_eyes = "heart_eyes"  # 😍
    disappointed = "disappointed"  # 😞
    poop = "poop"  # 💩
    skull = "skull"  # 💀
    neutral_face = "neutral_face"  # 😐

    # skip task system uses special emoji codes
    skip_reply = "_skip_reply"
    skip_ranking = "_skip_ranking"
    skip_labeling = "_skip_labeling"

class EmojiOp(str, enum.Enum):
    toggle = "toggle"
    add = "add"
    remove = "remove"

class RequestEmoji(BaseModel):
    op: EmojiOp = EmojiOp.toggle
    emoji: EmojiCode

class Emoji(Repository):
    def __init__(self, supabase_client):
        self.db = supabase_client
    
    def get_user_emoji_by_message_id(self, message_id: UUID, user_id: UUID):
        response = (
            self.db.from_("emoji")
            .select("*")
            .filter("message_id", "eq", message_id)
            .filter("user_id", "eq", user_id)
            .execute()
        )
        return response

    def get_user_emoji(self, user_id: UUID):
        response = (
            self.db.from_("emoji")
            .select("*")
            .filter("user_id", "eq", user_id)
            .execute()
        )
        return response
    
    def get_emoji_by_message_id(self, message_id: UUID):
        response = (
            self.db.from_("emoji")
            .select("*")
            .filter("message_id", "eq", message_id)
            .execute()
        )
        return response
    
    def get_emoji_for_message(self, user_id: UUID, message_id: UUID) -> MessageEmoji | None:
        response = (
            self.db.from_("emoji")
            .select("id:message_id, emoji, chat_history(id: message_id, user_message, assistant)")
            .filter("user_id", "eq", user_id)
            .filter("message_id", "eq", message_id)
            .execute()
        )
        if len(response.data) == 0:
                return MessageEmoji(
                    message_id=str(message_id),
                    emoji=None
                )
        message_emoji_data = response.data[0]
        return MessageEmoji(
            message_id=str(message_emoji_data["chat_history"]["id"]),
            emoji=message_emoji_data["emoji"]
        )
    
    def add_emoji(self, message_id, user_id, emoji: EmojiCode):
        response = (
            self.db.from_("emoji")
            .insert({"message_id": message_id, "user_id": user_id, "emoji": emoji})
            .execute()
        )
        return response

    def remove_emoji(self, message_id, user_id):
        response = (
            self.db.from_("emoji")
            .delete()
            .filter("message_id", "eq", message_id)
            .filter("user_id", "eq", user_id)
            .execute()
        )
        return response
    
    def check_emoji_exist(self, message_id: UUID, user_id: UUID, emoji) -> bool:
        logger.info(f"Check emoji exist: {message_id}, {user_id}, {emoji}")
        response = (
            self.db.from_("emoji")
            .select("*")
            .filter("message_id", "eq", message_id)
            .filter("user_id", "eq", user_id)
            .filter("emoji", "eq", emoji)
            .execute()
        )
        return len(response.data) > 0

