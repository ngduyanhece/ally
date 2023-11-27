from uuid import UUID

from app.models import get_supabase_db


def add_testcase_data_to_dataset(
        dataset_id: UUID, testcase_data_id: UUID):
    supabase_db = get_supabase_db()

    return supabase_db.create_dataset_testcase_data(
        dataset_id, testcase_data_id)
