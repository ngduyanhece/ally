from pathlib import Path

import modal
import pinecone
from core.settings import settings
from langchain_community.embeddings.openai import OpenAIEmbeddings
from langchain_community.vectorstores import Pinecone

ally_dir = Path(__file__).parent.parent

image = modal.Image.debian_slim(
		python_version="3.11"
).pip_install(
	"langchain",
	"openai==1.3.9",
	"pinecone-client==2.2.4",
	"supabase==1.1.1",
	"loguru",
	"pydantic==2.4.2",
	"pydantic-settings==2.0.3",
	"asyncpg==0.28.0",
	"python-multipart==0.0.6",
	"tiktoken==0.5.1"
)

stub = modal.Stub(
	name="ally-pinecone",
	image=image,
	mounts=[
		modal.Mount.from_local_file(ally_dir / '.env', remote_path="/root/.env")
	],
)

@stub.function(
	image=image,
	retries=3,
	container_idle_timeout=50,
	timeout=86400,
)
async def add_to_pinecone(
	agent_name: str,
	contents: list[str]
):
	pinecone.init(
		api_key=settings.pinecone_api_key,
		environment=settings.pinecone_environment
	)
	index = pinecone.Index(agent_name)
	embeddings = OpenAIEmbeddings(openai_api_key=settings.openai_api_key)
	pinecone_vector_db = Pinecone(index, embeddings, "text")
	try:
		ids = pinecone_vector_db.add_texts(
			texts=contents,
			batch_size=100,
			embedding_chunk_size=2000,
		)
	except Exception as e:
		raise e
	return ids