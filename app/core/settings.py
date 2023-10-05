from pydantic_settings import BaseSettings


class COREAPPSETTING(BaseSettings):
    
    supabase_url: str
    supabase_service_key: str
    pg_database_url: str
    openai_api_key: str
    pinecone_api_key: str
    pinecone_env: str
    anthropic_api_key: str
    jwt_secret_key: str
    authenticate: str
    celery_broker_url: str
    celebry_broker_queue_name: str
    private: str
    llm_model_path: str
    resend_api_key: str
    resend_email_address: str
    crawl_depth: str
    

settings = COREAPPSETTING(_env_file='.env', _env_file_encoding='utf-8')
