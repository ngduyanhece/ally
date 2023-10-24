from app.logger import get_logger
from app.models.chats import MessageLabel
from app.models.settings import get_supabase_db

logger = get_logger(__name__)


def crate_message_label_by_id(
    message_label: MessageLabel,
    message_id: str,
    user_id: str
) -> MessageLabel:
    supabase_db = get_supabase_db()
    message = supabase_db.get_message_by_id(message_id)
    if len(message.data) > 0:
        exist_message_label = supabase_db.get_message_label_by_id(message_id)
        if exist_message_label is not None:
            raise Exception("Message label already exists")
        return supabase_db.create_message_label_by_id(
            message_label, message_id, user_id)
    else:
        raise Exception("Message not found")
