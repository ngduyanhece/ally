import chainlit as cl
import pinecone
from core.settings import settings
from langchain_community.embeddings.openai import OpenAIEmbeddings
from langchain_community.vectorstores import Pinecone


async def retrieve_agent_memory_tool(query: str):
	agent_name = cl.user_session.get("chat_profile")
	pinecone.init(
		api_key=settings.pinecone_api_key,
		environment=settings.pinecone_environment
	)
	index = pinecone.Index(agent_name)
	embeddings = OpenAIEmbeddings(openai_api_key=settings.openai_api_key)
	pinecone_vector_db = Pinecone(index, embeddings, "text")
	docs = pinecone_vector_db.similarity_search(
		query=query,
		k=10,
	)
	content = [doc.page_content for doc in docs]
	return "\n".join(content)

retrieve_agent_memory_tool_interface = {
	"type": "function",
	"function": {
		"name": "retrieve_agent_memory_tool",
		"description": "retrieve agent memory from Ally Platform",
		"parameters": {
			"type": "object",
			"properties": {
				"query": {
					"type": "string",
					"description": "The query to search for the agent memory for example: hello world",
				}
			},
			"required": ["query"]
		},
	}
}