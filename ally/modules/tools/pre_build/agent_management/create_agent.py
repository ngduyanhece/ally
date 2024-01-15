import random

import chainlit as cl
import pinecone
from core.settings import get_supabase_client, settings
from modules.agent.dto.inputs import CreateAgentProperties, ModelTye
from modules.agent.entity.agent_entity import RoleEnum
from modules.agent.service.agent_service import AgentService
from modules.agent.service.agent_user_service import AgentUserService

agent_service = AgentService()
agent_user_service = AgentUserService()

# define the function here to avoid circular import


# python function to check if string is consist of lowercase alphanumeric characters or hyphens, and it must start and end with an alphanumeric character.
def is_valid_name(name: str):
	if len(name) < 3 or len(name) > 20:
		return False
	if name[0].isnumeric():
		return False
	if name[-1].isnumeric():
		return False
	for char in name:
		if not char.isalnum() and char != "-":
			return False
	return True


async def create_new_agent_tool(
	name: str,
	description: str,
	instructions: str):
	"""Create new agent in Ally Platform"""
	# check if name is valid
	if not is_valid_name(name):
		return """
			Agent name is not valid, please try again name must consist of lowercase
			alphanumeric characters or hyphens, and it must start and end with an alphanumeric character.
		"""
	db = get_supabase_client()
	base_icon_url = "https://myfirefly-ai.s3.amazonaws.com/ally_agent_avatar/{}.png"
	random_number = random.randint(1, 100)
	agent = CreateAgentProperties(
		name=name,
		description=description,
		icon=base_icon_url.format(random_number),
		instructions=instructions,
		model=ModelTye.gpt_4_turbo
	)
	user = cl.user_session.get("user")
	user_id = user.tags[0]
	try:
		# create a new agent
		new_agent = await agent_service.create_agent(agent)
		# create user agent relation
		agent_user_service.create_agent_user(
			user_id, new_agent.id, RoleEnum.Owner
		)
		# create agent memory
		pinecone.init(
			api_key=settings.pinecone_api_key,
			environment=settings.pinecone_environment
		)
		pinecone.create_index(
			name=name,
			dimension=1536,
		)

		# allow agent to use retrieve agent memory tool
		# create new entry in agents_tools table
		retrieve_agent_memory_tool_id = db.from_("tools").select(
			"id"
		).eq(
			"name", "retrieve_agent_memory_tool"
		).execute().get("id")
		update_agent_memory_tool_id = db.from_("tools").select(
			"id"
		).eq(
			"name", "update_agent_memory_tool"
		).execute().get("id")

		db.from_("agents_tools").insert(
			{
				"agent_id": new_agent.id,
				"tool_id": retrieve_agent_memory_tool_id,
			}
		).execute()
		db.from_("agents_tools").insert(
			{
				"agent_id": new_agent.id,
				"tool_id": update_agent_memory_tool_id,
			}
		).execute()
		return "Agent {agent} created successfully please reload your page to start using your new agent".format(agent=new_agent.name)
	except Exception as e:
		return "Agent {agent} created failed with unexpected error: {error}".format(
			agent=new_agent.name, error=e)

create_new_agent_tool_interface = {
	"type": "function",
	"function": {
		"name": "create_new_agent_tool",
		"description": "create new agent in Ally Platform",
		"parameters": {
			"type": "object",
			"properties": {
				"name": {
					"type": "string",
					"description": "The name of the agent for example: funny ally name must consist of lowercase alphanumeric characters or hyphens, and it must start and end with an alphanumeric character. the name of agent must be unique and can not be changed after creation so choose wisely",
				},
				"description": {
					"type": "string",
					"description": "The description of the agent for example: this agent is funny",
				},
				"instructions": {
					"type": "string",
					"description": "the instruction for the agent",
				}
			},
			"required": ["name", "description", "instructions"]
		},
	}
}
