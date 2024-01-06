import chainlit as cl
import modal
from langchain.text_splitter import CharacterTextSplitter


async def update_agent_memory_tool(content: str):
	agent_name = cl.user_session.get("chat_profile")

	text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
	docs = text_splitter.create_documents([content])
	contents = [doc.page_content for doc in docs]

	add_to_pinecone = modal.Function.lookup("ally-pinecone", "add_to_pinecone")
	call = add_to_pinecone.spawn(agent_name, contents)
	return "your agent memory has been updated"

update_agent_memory_tool_interface = {
	"type": "function",
	"function": {
		"name": "update_agent_memory_tool",
		"description": "update memory for agent in Ally Platform",
		"parameters": {
			"type": "object",
			"properties": {
				"content": {
					"type": "string",
					"description": "The content to add to the agent memory for example based on the conversation with the user",
				}
			},
			"required": ["content"]
		},
	}
}
