import chainlit as cl

from ally.modules.agent.service.agent_service import AgentService

agent_service = AgentService()

def init_chainlit_actions():
	@cl.action_callback("delete_agent")
	async def delete_agent(action):
		agent_name = cl.user_session.get("chat_profile")
		agent = agent_service.get_agent_by_name(agent_name)
		response = await agent_service.delete_agent(agent.id)
		if response is None:
			await cl.Message(content="Agent not found").send()
			return
		await cl.Message(content="Agent deleted successfully").send()
		await action.remove()