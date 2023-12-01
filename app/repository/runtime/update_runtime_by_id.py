from uuid import UUID

from app.models import get_supabase_db
from app.models.databases.supabase.runtimes import CreateRuntimeProperties
from app.models.runtimes import RuntimeEntity


def update_runtime_by_id(
		runtime_id: UUID, runtime: CreateRuntimeProperties) -> RuntimeEntity:
	"""Update a runtime by id"""
	supabase_db = get_supabase_db()

	return supabase_db.update_runtime_by_id(runtime_id, runtime)
