from pathlib import Path

import modal

from app.llm.llm_brain import LLMBrain
from app.models.chats import ChatInput

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
)

stub = modal.Stub(
	name="brain-chat",
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
def brain_chat(
	chat_id: str,
	model: str,
	max_tokens: int,
	temperature: float,
	brain_id: str,
	user_openai_api_key: str,
	prompt_id: str,
	chat_input: ChatInput
):
	llm_brain = LLMBrain(
		chat_id=chat_id,
		model=model,
		max_tokens=max_tokens,
		temperature=temperature,
		brain_id=brain_id,
		user_openai_api_key=user_openai_api_key,
		prompt_id=prompt_id,
	)
	return llm_brain.generate_answer(chat_id, chat_input)


@stub.local_entrypoint()
def main():
	chat_input = ChatInput(
		chat_input="hello",
		use_history=True,
		model="gpt-3.5-turbo",
		temperature=0.7,
		max_tokens=250,
		brain_id=None,
		prompt_id=None,
	)
	chat_id = "5909ed00-b882-467f-ae31-84c8f4fbc618"
	brain_id = "0f24e329-84a2-4abe-9ee5-043e31822adb"
	user_openai_api_key = "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"
	print(brain_chat.remote(
		chat_id=chat_id,
		model=chat_input.model,
		max_tokens=chat_input.max_tokens,
		temperature=chat_input.temperature,
		brain_id=brain_id,
		user_openai_api_key=user_openai_api_key,
		prompt_id=str(chat_input.prompt_id),
		chat_input=chat_input)
	)

