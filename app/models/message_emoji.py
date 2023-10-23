from typing import Optional

from pydantic import BaseModel


class MessageEmoji(BaseModel):
    message_id: Optional[str]
    emoji: Optional[str]
