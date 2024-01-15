import chainlit as cl
from modules.agent.service.agent_user_service import AgentUserService

agent_user_service = AgentUserService()


async def get_all_agents_tool():
	"""Create new agent in Ally Platform"""
	user = cl.user_session.get("user")
	user_id = user.tags[0]
	response = agent_user_service.get_user_agents(user_id)
	agents = []
	for agent in response:
		agents.append(
			{
				"id": agent.id,
				"name": agent.name,
				"instructions": agent.instructions,
				"rights": agent.rights,
			}
		)
	return str(agents)

get_all_agents_tool_interface: dict = {
	"type": "function",
	"function": {
		"name": "get_all_agents_tool",
		"description": "get all agents for current user in Ally Platform",
		"parameters": {
		},
	}
}
