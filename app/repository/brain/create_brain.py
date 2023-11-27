from app.models import BrainEntity, get_supabase_db
from app.models.databases.supabase.brains import CreateFullBrainProperties


def create_brain(brain: CreateFullBrainProperties) -> BrainEntity:
    supabase_db = get_supabase_db()

    return supabase_db.create_brain(brain)
