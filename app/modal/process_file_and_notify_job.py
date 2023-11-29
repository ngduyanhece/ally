from pathlib import Path

import modal

from app.modules.file.service.file_service import FileService

ally_dir = Path(__file__).parent.parent.parent

file_service = FileService()

image = modal.Image.debian_slim(
		python_version="3.10"
).pip_install(
	"fastapi==0.103.2",
	"langchain==0.0.325",
	"pydantic==2.4.2",
	"pydantic-settings==2.0.3",
	"supabase==1.1.1",
	"asyncpg==0.28.0",
	"python-multipart==0.0.6",
	"openai==0.28.1",
	"PyMuPDF==1.23.4",
	"tiktoken==0.5.1",
	"tqdm==4.66.1",
	"pandas==2.1.2",
	"unstructured==0.11.0",
	"pdf2image==1.16.3",
	"pypdf==3.17.1",
	"opencv-python==4.8.1.78",
	"pdfminer.six==20221105",
	"unstructured_pytesseract==0.3.12",
	"unstructured_inference==0.7.16",
	"python-pptx==0.6.23"
).run_commands("apt-get update && apt-get install ffmpeg libsm6 libxext6  -y")

stub = modal.Stub(
	name="file-process-and-notify",
	image=image,
	mounts=[
		modal.Mount.from_local_file(ally_dir / '.env', remote_path="/root/.env")
	],
)

@stub.function(
	image=image,
	retries=3,
	container_idle_timeout=50
)
async def file_process_and_notify(
	file_name,
	file_original_name,
	brain_id,
	notification_id,
):
	await file_service.process_file_and_notify(
		file_name=file_name,
		file_original_name=file_original_name,
		brain_id=brain_id,
		notification_id=notification_id if notification_id else None,
	)
