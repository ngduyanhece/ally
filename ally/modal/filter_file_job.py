from pathlib import Path

import modal
from chainlit import File
from packages.files.processors import filter_file

ally_dir = Path(__file__).parent.parent

image = modal.Image.debian_slim(
		python_version="3.11"
).pip_install(
	"langchain",
	"pydantic==2.4.2",
	"pydantic-settings==2.0.3",
	"asyncpg==0.28.0",
	"python-multipart==0.0.6",
	"openai==1.3.9",
	"PyMuPDF==1.23.4",
	"tiktoken==0.5.1",
	"unstructured==0.11.0",
	"pdf2image==1.16.3",
	"pypdf==3.17.1",
	"opencv-python==4.8.1.78",
	"pdfminer.six==20221105",
	"unstructured_pytesseract==0.3.12",
	"unstructured_inference==0.7.16",
	"python-pptx==0.6.23",
	"newspaper3k",
	"beautifulsoup4",
	"chainlit==0.7.700",
	"pinecone-client==2.2.4",
	"supabase==1.1.1",
	"loguru"
).run_commands("apt-get update && apt-get install ffmpeg libsm6 libxext6  -y")

stub = modal.Stub(
	name="ally",
	image=image,
	mounts=[
		modal.Mount.from_local_file(ally_dir /  '.env', remote_path="/root/.env")
	],
)

@stub.function(
	image=image,
	retries=3,
	container_idle_timeout=50,
	timeout=86400,
)
async def filter_file_func(
	file_element: File,
	agent_name: str,
):
	response = await filter_file(file_element, agent_name)
	return response