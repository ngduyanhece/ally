from uuid import UUID

from app.models import get_supabase_db
from app.models.databases.supabase.runtimes import CreateRuntimeProperties
from app.models.runtimes import RuntimeEntity


def create_runtime(
        runtime: CreateRuntimeProperties, user_id: UUID) -> RuntimeEntity:
    supabase_db = get_supabase_db()

    return supabase_db.create_runtime(runtime, user_id)
