import chainlit as cl

from ally.modules.agent.dto.inputs import AgentUpdatableProperties
from ally.modules.agent.service.agent_service import AgentService

agent_service = AgentService()

def init_chainlit_settings():
	"""
	Initializes the chainlit settings.
	"""
	@cl.on_settings_update
	async def setup_agent(settings):
		agent_name = cl.user_session.get("chat_profile")
		agent = agent_service.get_agent_by_name(agent_name)
		name = settings.get("agent_name")
		instructions = settings.get("instructions")
		agent_model = settings.get("agent_model")

		agent_update_values = AgentUpdatableProperties(
			name=name,
			instructions=instructions,
			model=agent_model
		)

		response = await agent_service.update_agent_by_id(
			agent.id, agent_update_values)
		if response is None:
			await cl.Message(content="Agent not found").send()
			return
		agent_service.update_agent_last_update_time(agent.id)
		await cl.Message(content="Agent updated successfully").send()
    
	