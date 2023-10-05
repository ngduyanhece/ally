from app.models import BrainEntity, get_supabase_db
from app.models.databases.supabase.brains import CreateBrainProperties


def create_brain(brain: CreateBrainProperties) -> BrainEntity:
    supabase_db = get_supabase_db()

    return supabase_db.create_brain(brain)
