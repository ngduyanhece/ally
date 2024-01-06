
from typing import List

from core.settings import get_supabase_client
from modules.agent.entity.agent_entity import ToolEntity
from modules.agent.repository.interfaces.agents_tools_interface import \
    AgentToolInterface


class AgentsTools(AgentToolInterface):
	
	def __init__(self):
		supabase_client = get_supabase_client()
		self.db = supabase_client
	
	def get_tools_for_agent(
		self,
		agent_id: str
	) -> List[ToolEntity]:
		"""
		get all tools for a agent
		"""
		response = (
			self.db.from_("agents_tools")
			.select(
				"tool_id, tools (id, name)"
			)
			.filter("agent_id", "eq", agent_id)
			.execute()
		)
		agent_tools: List[ToolEntity] = []
		for tool in response.data:
			agent_tools.append(
				ToolEntity(
					id=tool["tools"]["id"],
					name=tool["tools"]["name"]
				)
			)
		return agent_tools
		