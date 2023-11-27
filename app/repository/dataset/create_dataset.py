from uuid import UUID

from app.models import get_supabase_db
from app.models.databases.supabase.dataset import CreateDatasetProperties
from app.models.dataset import DatasetEntity


def create_dataset(
        dataset: CreateDatasetProperties, user_id: UUID) -> DatasetEntity:
    supabase_db = get_supabase_db()

    return supabase_db.create_dataset(dataset, user_id)
