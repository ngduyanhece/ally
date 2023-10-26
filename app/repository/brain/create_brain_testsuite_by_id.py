from uuid import UUID

from app.models import get_supabase_db
from app.models.brain_testsuite import BrainTestSuiteEntity
from app.models.databases.supabase.brains import CreateBrainTestsuiteProperties


def create_brain_testsuite_by_id(
    brain_id: UUID,
    brain_testsuite: CreateBrainTestsuiteProperties
) -> BrainTestSuiteEntity:
    supabase_db = get_supabase_db()
    existing_brain_testsuite = supabase_db.get_brain_testsuite_by_id(brain_id)
    if existing_brain_testsuite:
        return None
    return supabase_db.create_brain_testsuite_by_id(brain_id, brain_testsuite)
