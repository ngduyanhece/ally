from uuid import UUID

from app.models import get_supabase_db
from app.models.dataset import DatasetEntity


def get_dataset(dataset_id: UUID, user_id: UUID) -> DatasetEntity | None:
	"""
	Get a dataset by its id

	Args:
			dataset_id (UUID): The id of the dataset

	Returns:
			DatasetEntity: The dataset
	"""
	supabase_db = get_supabase_db()
	return supabase_db.get_dataset(dataset_id, user_id)
