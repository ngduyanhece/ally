from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import SupabaseVectorStore
from pydantic_settings import BaseSettings
from supabase.client import Client, create_client


class COREAPPSETTING(BaseSettings):
	supabase_url: str
	supabase_service_key: str
	openai_api_key: str
	jwt_secret_key: str
	crawl_depth: str
	authenticate: bool
	

settings = COREAPPSETTING(_env_file='.env', _env_file_encoding='utf-8')

def get_supabase_client() -> Client:
	settings = COREAPPSETTING(_env_file='.env', _env_file_encoding='utf-8')
	supabase_client: Client = create_client(
		settings.supabase_url, settings.supabase_service_key
	)
	return supabase_client

def get_embeddings() -> OpenAIEmbeddings:
	embeddings = OpenAIEmbeddings(
			openai_api_key=settings.openai_api_key
	)
	return embeddings

def get_documents_vector_store() -> SupabaseVectorStore:
	embeddings = get_embeddings()
	supabase_client: Client = create_client(
		settings.supabase_url, settings.supabase_service_key
	)
	documents_vector_store = SupabaseVectorStore(
		supabase_client, embeddings, table_name="vectors"
	)
	return documents_vector_store
