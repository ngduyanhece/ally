from pydantic_settings import BaseSettings
from supabase.client import Client, create_client

from app.core.settings import settings
from app.models.databases.supabase.supabase import SupabaseDB


class BrainSettings(BaseSettings):
    openai_api_key: str
    anthropic_api_key: str
    supabase_url: str
    supabase_service_key: str
    pg_database_url: str = "not implemented"
    resend_api_key: str = "null"
    resend_email_address: str = "andy@open-lab.io"


def get_supabase_client() -> Client:
    # TODO we should include the supabase_url and supabase_service_key in the brain setting
    supabase_client: Client = create_client(
        settings.supabase_url, settings.supabase_service_key
    )
    return supabase_client

def get_supabase_db() -> SupabaseDB:
    supabase_client = get_supabase_client()
    return SupabaseDB(supabase_client)
