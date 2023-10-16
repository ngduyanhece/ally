from app.models import get_supabase_db
from app.models.meta_brain_entity import PublicMetaBrain


def get_public_meta_brains() -> list[PublicMetaBrain]:
    supabase_db = get_supabase_db()
    return supabase_db.get_public_meta_brains()
