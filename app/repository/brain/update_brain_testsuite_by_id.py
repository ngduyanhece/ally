from app.models import get_supabase_db
from app.models.brain_testsuite import BrainTestSuiteEntity
from app.models.databases.supabase.brains import UpdateBrainTestsuiteProperties


def update_brain_testsuite_by_id(
    brain_id: str,
    brain_testsuite: UpdateBrainTestsuiteProperties
) -> BrainTestSuiteEntity:
    supabase_db = get_supabase_db()
    response = supabase_db.update_brain_testsuite_by_id(brain_id, brain_testsuite)
    if response:
        supabase_db.update_brain_testsuite_last_update_time(brain_id)
    return response
