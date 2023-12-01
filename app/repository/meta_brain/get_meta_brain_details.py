from uuid import UUID

from app.models.meta_brain_entity import MetaBrainEntity
from app.models.settings import get_supabase_client


def get_meta_brain_details(meta_brain_id: UUID) -> MetaBrainEntity | None:
    supabase_client = get_supabase_client()
    response = (
        supabase_client.table("meta_brains")
        .select("*")
        .filter("meta_brain_id", "eq", str(meta_brain_id))
        .execute()
    )
    if response.data == []:
        return None
    return MetaBrainEntity(**response.data[0])
