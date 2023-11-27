from pathlib import Path
from uuid import UUID

import modal

from app.llm.brain_agent import BrainAgent
from app.repository.brain.get_brain_by_id import get_brain_by_id

ally_dir = Path(__file__).parent.parent.parent

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
	name="zalo-me-agent-learn",
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
def zalo_me_agent_learn(
	testcase_data_id: UUID,
):
	chat_id = "00302f06-2f37-4311-a72f-1c72adb61cdc"
	brain_id = "009e2d94-a96a-4e7c-ba9f-271c80edcafd"
	brain_details = get_brain_by_id(brain_id)
	brain_agent = BrainAgent(
		brain_details=brain_details
	)
	answer = brain_agent.learn(
		chat_id=chat_id,
		testcase_data_id=testcase_data_id
	)
	return answer
	
	