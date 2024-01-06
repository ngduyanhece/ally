import os
from pathlib import Path

current_path = Path(__file__).parent

os.environ[
	"GOOGLE_APPLICATION_CREDENTIALS"
] = os.path.join(current_path, 'lyrical-link-410013-f50a7a2dad72.json')

async def ask_gemini_tool(prompt: str):
	import vertexai
	from vertexai.preview.generative_models import ChatSession, GenerativeModel
	vertexai.init(project="lyrical-link-410013", location="asia-southeast1")
	model = GenerativeModel("gemini-pro")
	chat = model.start_chat()

	def get_chat_response(chat: ChatSession, prompt: str) -> str:
		response = chat.send_message(prompt)
		return response.text
	
	return get_chat_response(chat, prompt)


ask_gemini_tool_interface = {
	"type": "function",
	"function": {
		"name": "ask_gemini_tool",
		"description": "ask gemini which is a language model trained by google to get the information that agent doesn't know",
		"parameters": {
			"type": "object",
			"properties": {
				"prompt": {
					"type": "string",
					"description": "the sufficient prompt to ask gemini about the information that agent doesn't know",
				}
			},
			"required": ["prompt"]
		},
	}
}