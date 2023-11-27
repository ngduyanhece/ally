from uuid import UUID

from app.models import get_supabase_db
from app.models.dataset import DatasetEntity


def get_user_datasets(user_id: UUID) -> list[DatasetEntity]:
    """
    List all user dataset
    """
    supabase_db = get_supabase_db()
    return supabase_db.get_user_datasets(user_id)