import os
from pathlib import Path

current_path = Path(__file__).parent

os.environ[
	"GOOGLE_APPLICATION_CREDENTIALS"
] = os.path.join(current_path, 'lyrical-link-410013-f50a7a2dad72.json')


async def publish_content_to_avoca_tool(content_to_generate: str, type: str):
	import vertexai
	from vertexai.preview.generative_models import ChatSession, GenerativeModel
	vertexai.init(project="lyrical-link-410013", location="asia-southeast1")
	model = GenerativeModel("gemini-pro")
	chat = model.start_chat()

	def get_chat_response(chat: ChatSession, prompt: str) -> str:
		response = chat.send_message(prompt)
		return response.text

	if type == "quiz":
			prompt = f"""Generate a quiz about {content_to_generate} by the following JSON format:"""
			format = """
				{
					"title": "title of the quiz",
					"avoca": True,
					"type": "quiz",
					"status": "unpublished",
					"min_required_question": None,
					"mission_data": [
						{
							"index_sort": 1,
							"question": "content of the question",
							"question_type": "pick",
							"type_selected": "single",
							"pick": [
								{
									"is_correct": True,
									"option": "value of the option here"
								},
								...
							]
						},
						...
					]
				}'
			"""
			prompt += format
	if type == "open_ended":
		prompt = f"""Generate text responses to open-ended questions about {content_to_generate}."""
		format = """
			The questions are in the following JSON format:
			{
				"title": "title of the open ended",
				"avoca": True,
				"type": "survey",
				"status": "unpublished",
				"mission_data": [
					{
						"index_sort": 1,
						"question": "content of the question",
						"question_type": "text"
					},
					...
				]
			}
		"""
		prompt += format
	response =  get_chat_response(chat, prompt)


publish_content_to_avoca_tool_interface = {
	"type": "function",
	"function": {
		"name": "publish_content_to_avoca_tool",
		"description": "publish content to avoca tool this tool only works when the user explicitly asks for it",
		"parameters": {
			"type": "object",
			"properties": {
				"content_to_generate": {
					"type": "string",
					"description": "the content to generate",
				},
				"type": {
					"type": "string",
					"description": "the type of content to generate and the possible values are: quiz or open_ended",
				}
			},
			"required": ["type"]
		},
	}
}