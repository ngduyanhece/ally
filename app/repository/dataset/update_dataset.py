from uuid import UUID

from app.models import get_supabase_db
from app.models.databases.supabase.dataset import CreateDatasetProperties
from app.models.dataset import DatasetEntity


def update_dataset(
        dataset: CreateDatasetProperties, dataset_id: UUID, user_id: UUID) -> DatasetEntity:
    supabase_db = get_supabase_db()

    return supabase_db.update_dataset(dataset, dataset_id, user_id)
