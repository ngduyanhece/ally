from app.logger import get_logger
from app.models.settings import get_supabase_db
from app.models.testcase_data import TestCaseDataEntity

logger = get_logger(__name__)


def create_testcase_data_from_message(
    message_id: str,
    description: str,
) -> TestCaseDataEntity:
    supabase_db = get_supabase_db()
    raw_message = supabase_db.get_message_by_id(message_id).data[0]
    if len(raw_message) == 0:
        raise ValueError("Message not found")
    message_with_label = supabase_db.get_message_label_by_id(message_id)
    if message_with_label is None:
        raise ValueError("Message label not found")
    response = supabase_db.create_testcase_data_from_message(
        description=description,
        input=raw_message["user_message"],
        reference_output=message_with_label.label,
        context=message_with_label.feedback,
    )
    return TestCaseDataEntity(**response.data[0])