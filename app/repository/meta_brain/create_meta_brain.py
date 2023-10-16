from app.models.databases.supabase.meta_brains import CreateMetaBrainProperties
from app.models.meta_brain_entity import MetaBrainEntity
from app.models.settings import get_supabase_db


def create_meta_brain(meta_brain: CreateMetaBrainProperties) -> MetaBrainEntity:
    supabase_db = get_supabase_db()

    return supabase_db.create_meta_brain(meta_brain)
