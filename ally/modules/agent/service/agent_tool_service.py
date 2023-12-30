from openai import AsyncOpenAI

from ally.core.settings import settings
from ally.logger import get_logger
from ally.modules.agent.repository.agents_tools import AgentsTools
from ally.modules.agent.service.agent_service import AgentService
from ally.modules.tools.load_tools import _TOOL_INTERFACE_MAP

logger = get_logger(__name__)

agent_service = AgentService()


class AgentToolService:
	
	def __init__(self):
		self.agent_tool_repository = AgentsTools()
	
	def get_tools_for_agent(
		self,
		agent_id: str
	):
		return self.agent_tool_repository.get_tools_for_agent(agent_id)
	
	async def update_tools_for_agent(
		self,
		agent_id: str,
	) -> dict | None:
		tools = self.get_tools_for_agent(agent_id)
		tool_names = [tool.name for tool in tools]
		agent_tools = [{"type": "code_interpreter"}]
		for tool_name in tool_names:
			tool_interface = _TOOL_INTERFACE_MAP.get(tool_name)
			if tool_interface is not None:
				agent_tools.append(tool_interface)
		logger.info("agent_tools: %s", agent_tools)
		existed_agent = agent_service.get_agent_by_id(agent_id)
		if existed_agent is None:
			return None
		client = AsyncOpenAI(api_key=settings.openai_api_key)
		await client.beta.assistants.update(
			assistant_id=agent_id,
			instructions=existed_agent.instructions,
			name=existed_agent.name,
			model=existed_agent.model,
			tools=agent_tools,
		)
		return {'message': 'Tools updated successfully for agent {agent_id}'.format(agent_id=agent_id)}