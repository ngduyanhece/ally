import chainlit as cl

from ally.modules.agent.dto.inputs import CreateAgentProperties, ModelTye
from ally.modules.agent.entity.agent_entity import RoleEnum
from ally.modules.agent.service.agent_service import AgentService
from ally.modules.agent.service.agent_user_service import AgentUserService

agent_service = AgentService()
agent_user_service = AgentUserService()


async def create_new_agent_tool(name: str, instructions: str):
	"""Create new agent in Ally Platform"""
	agent = CreateAgentProperties(
		name=name,
		instructions=instructions,
		model=ModelTye.gpt_4_turbo
	)
	user = cl.user_session.get("user")
	user_id = user.tags[0]
	try:
		new_agent = await agent_service.create_agent(agent)
		agent_user_service.create_agent_user(
			user_id, new_agent.id, RoleEnum.Owner
		)
		return "Agent {agent} created successfully".format(agent=new_agent.name)
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
					"description": "The name of the agent for example: funny ally",
				},
				"instructions": {
					"type": "string",
					"description": "the instruction for the agent",
				}
			},
			"required": ["name", "instructions"]
		},
	}
}
