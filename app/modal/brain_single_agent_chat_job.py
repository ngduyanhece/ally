from pathlib import Path
from uuid import UUID

import modal

from app.llm.brain_agent import BrainAgent
from app.models.chats import BrainAgentInput
from app.modules.brain.entity.brain import FullBrainEntityWithRights
from app.modules.brain.service.brain_service import BrainService

ally_dir = Path(__file__).parent.parent.parent
brain_service = BrainService()

image = modal.Image.debian_slim(
		python_version="3.11"
).pip_install(
	"fastapi==0.103.2",
	"pydantic==2.4.2",
	"pydantic-settings==2.0.3",
	"supabase==1.1.1",
	"asyncpg==0.28.0",
	"python-multipart==0.0.6",
	"openai==1.3.9",
	"PyMuPDF==1.23.4",
	"tiktoken==0.5.1",
	"tqdm==4.66.1",
	"pandas==2.1.2",
	"beautifulsoup4",
	"newspaper3k",
	"langchain==0.0.350",
	"langchain-core==0.1.1",
	"langchain_community==0.0.3",
	"google-api-python-client==2.110.0",
	"thefuzz"
)

stub = modal.Stub(
	name="single-agent-chat",
	image=image,
	mounts=[
		modal.Mount.from_local_file(ally_dir / '.env', remote_path="/root/.env")
	],
)

@stub.function(
	image=image,
	retries=3,
	container_idle_timeout=50,
	secret=modal.Secret.from_name("openai-secret")
)
def single_agent_chat(
	chat_id: UUID,
	brain_details: FullBrainEntityWithRights,
	input: BrainAgentInput,
):
	brain_agent = BrainAgent(
		brain_details=brain_details
	)
	answer = brain_agent.generate_answer(chat_id=chat_id, input=input)
	return answer

@stub.local_entrypoint()
def main():
	chat_id = "f16fd0b5-3e26-4f9e-8dcc-871832a436cc"
	brain_id = "3e467f36-84fb-4257-837e-74da7def149a"
	brain_details = brain_service.get_brain_details(brain_id)
	input = BrainAgentInput(
		text_input="question: 8 dm2 24 cm2 = ……… dm2. Số thích hợp điền vào chỗ chấm là: choices:['A. 824', 'B. 82,4', 'C. 8,24', 'D. 0,824']",
	)
	answer = single_agent_chat.remote(
		chat_id=chat_id, brain_details=brain_details, input=input)
	print(answer)