from uuid import UUID

from app.models import get_supabase_db
from app.models.runtimes import RuntimeEntity


def delete_runtime_by_id(runtime_id: UUID) -> RuntimeEntity:
	"""
	Delete a runtime by id
	Args:
		runtime_id (UUID): The id of the runtime

	Returns:
		Runtime: The runtime
	"""
	supabase_db = get_supabase_db()
	return supabase_db.delete_runtime_by_id(runtime_id)
