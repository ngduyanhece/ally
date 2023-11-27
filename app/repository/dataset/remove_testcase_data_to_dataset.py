from uuid import UUID

from app.models import get_supabase_db


def remove_testcase_data_to_dataset(
        dataset_id: UUID, testcase_data_id: UUID, user_id: UUID):
    supabase_db = get_supabase_db()

    return supabase_db.delete_dataset_testcase_data(
        dataset_id, testcase_data_id, user_id)
