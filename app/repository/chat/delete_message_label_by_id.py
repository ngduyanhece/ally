from app.logger import get_logger
from app.models.settings import get_supabase_db

logger = get_logger(__name__)


def delete_message_label_by_id(
    message_id: str,
    user_id: str
):
    supabase_db = get_supabase_db()
    message = supabase_db.get_message_by_id(message_id)
    if len(message.data) > 0:
        exist_message_label = supabase_db.get_message_label_by_id(message_id)
        if exist_message_label:
            return supabase_db.delete_message_label_by_id(message_id, user_id)
        else:   
            raise Exception("Message label not found")
    else:
        raise Exception("Message not found")
