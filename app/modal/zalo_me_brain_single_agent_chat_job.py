from pathlib import Path

import modal

from app.llm.brain_agent import BrainAgent
from app.models.chats import BrainAgentInput
from app.repository.brain import get_brain_by_id

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
	name="zalo-me-agent-chat",
	image=image,
	mounts=[
		modal.Mount.from_local_file(ally_dir / '.env', remote_path="/root/.env")
	],
)

@stub.function(
	image=image,
	retries=1,
	container_idle_timeout=200
)
def zalo_me_agent_chat(
	input: BrainAgentInput,
):
	chat_id = "00302f06-2f37-4311-a72f-1c72adb61cdc"
	brain_id = "009e2d94-a96a-4e7c-ba9f-271c80edcafd"
	brain_details = get_brain_by_id(brain_id)
	brain_agent = BrainAgent(
		brain_details=brain_details
	)
	answer = brain_agent.generate_answer(chat_id=chat_id, input=input)
	return answer

@stub.local_entrypoint()
def main():

	input = BrainAgentInput(
		text_input="question: 8 dm2 24 cm2 = ……… dm2. Số thích hợp điền vào chỗ chấm là: choices:['A. 824', 'B. 82,4', 'C. 8,24', 'D. 0,824']",
	)
	answer = zalo_me_agent_chat.remote(input=input)
	print(answer)