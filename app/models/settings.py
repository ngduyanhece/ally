from langchain.embeddings.openai import OpenAIEmbeddings
from pydantic_settings import BaseSettings
from supabase.client import Client, create_client

from app.core.settings import settings
from app.models.databases.supabase.supabase import SupabaseDB
from app.vectorstore.supabase import CustomSupabaseVectorStore


class BrainSettings(BaseSettings):
    openai_api_key: str
    anthropic_api_key: str
    supabase_url: str
    supabase_service_key: str
    pg_database_url: str = "not implemented"
    resend_api_key: str = "re_C2E5atQy_45Kmu4pkx1rrqscRML9BThFE"
    resend_email_address: str = "onboarding@resend.dev"


def get_supabase_client() -> Client:
    # TODO we should include the supabase_url and supabase_service_key in the brain setting
    supabase_client: Client = create_client(
        settings.supabase_url, settings.supabase_service_key
    )
    return supabase_client

def get_supabase_db() -> SupabaseDB:
    supabase_client = get_supabase_client()
    return SupabaseDB(supabase_client)


def get_embeddings() -> OpenAIEmbeddings:
    # settings = BrainSettings()  # pyright: ignore reportPrivateUsage=none
    embeddings = OpenAIEmbeddings(
        openai_api_key=settings.openai_api_key
    )  # pyright: ignore reportPrivateUsage=none
    return embeddings


def get_documents_vector_store() -> CustomSupabaseVectorStore:
    # settings = BrainSettings()  # pyright: ignore reportPrivateUsage=none
    embeddings = get_embeddings()
    supabase_client: Client = create_client(
        settings.supabase_url, settings.supabase_service_key
    )
    documents_vector_store = CustomSupabaseVectorStore(
        supabase_client, embeddings, table_name="vectors"
    )
    return documents_vector_store