from app.logger import get_logger
from app.models.chats import MessageLabelOutput
from app.models.settings import get_supabase_db

logger = get_logger(__name__)


def get_message_label_by_id(
    message_id: str
) -> MessageLabelOutput | None:
    supabase_db = get_supabase_db()
    response = supabase_db.get_message_label_by_id(message_id)
    return response