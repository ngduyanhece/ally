from pathlib import Path
from uuid import UUID

import modal

from ally.utils.logs import print_text
from app.llm.brain_agent import BrainAgent
from app.modules.brain.entity.brain import FullBrainEntityWithRights
from app.modules.brain.service.brain_service import BrainService

ally_dir = Path(__file__).parent.parent.parent
brain_service = BrainService()

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
	"pandas==2.1.2"
)

stub = modal.Stub(
	name="single-agent-learn",
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
def single_agent_learn(
	chat_id: UUID,
	testcase_data_id: UUID,
	brain_details: FullBrainEntityWithRights,
):
	brain_agent = BrainAgent(
		brain_details=brain_details
	)
	answer = brain_agent.learn(
		chat_id=chat_id,
		testcase_data_id=testcase_data_id
	)
	return answer

@stub.local_entrypoint()
def main():
	chat_id = "f16fd0b5-3e26-4f9e-8dcc-871832a436cc"
	testcase_data_id = "142ea65e-8808-4253-b5b9-7c6459b187c6"
	brain_id = "3e467f36-84fb-4257-837e-74da7def149a"
	brain_details = brain_service.get_brain_details(brain_id)
	answer = single_agent_learn.remote(
		chat_id=chat_id,
		testcase_data_id=testcase_data_id,
		brain_details=brain_details
	)
	print_text(answer, style="bold green")
	
	