import pinecone
from core.settings import settings


async def create_agent_memory_tool(agent_name: str):
	pinecone.init(
		api_key=settings.pinecone_api_key,
		environment=settings.pinecone_environment
	)
	try:
		pinecone.create_index(
			name=agent_name,
			dimension=1536,
		)
	except Exception as e:
		return "error creating agent memory {e}".format(e=e)
	
	return str(pinecone.describe_index(name=agent_name))

create_agent_memory_tool_interface = {
	"type": "function",
	"function": {
		"name": "create_agent_memory_tool",
		"description": "create memory for agent in Ally Platform",
		"parameters": {
			"type": "object",
			"properties": {
				"agent_name": {
					"type": "string",
					"description": "The id of the agent for example: asst_ZJ905tH4bTPjKkxK7F3m6csN",
				}
			},
			"required": ["agent_name"]
		},
	}
}
