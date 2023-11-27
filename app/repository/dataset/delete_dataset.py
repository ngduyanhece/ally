from uuid import UUID

from app.models import get_supabase_db
from app.models.dataset import DatasetEntity


def delete_dataset(dataset_id: UUID, user_id: UUID) -> DatasetEntity:
    supabase_db = get_supabase_db()

    return supabase_db.delete_dataset(dataset_id, user_id)

