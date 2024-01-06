

from datetime import datetime

from core.settings import get_supabase_client, settings
from logger import get_logger
from modules.agent.dto.inputs import (AgentUpdatableProperties,
                                      CreateAgentProperties)
from modules.agent.entity.agent_entity import AgentEntity
from modules.agent.repository.interfaces.agents import AgentsInterface
from openai import AsyncOpenAI

logger = get_logger(__name__)

class Agents(AgentsInterface):
	
	def __init__(self):
		supabase_client = get_supabase_client()
		self.db = supabase_client
	
	async def create_agent(self, agent: CreateAgentProperties) -> AgentEntity:
		"""
		Create a agent
		"""
		client = AsyncOpenAI(api_key=settings.openai_api_key)
		assistant = await client.beta.assistants.create(
			name=agent.name,
			description=agent.description,
			instructions=agent.instructions,
			model=agent.model,
		)
		
		response = self.db.from_("agents").insert(
			{
				"id": assistant.id,
				"name": agent.name,
				"description": agent.description,
				"icon": agent.icon,
				"instructions": agent.instructions,
				"model": agent.model,
			}
		).execute()
		return AgentEntity(**response.data[0])
	
	def get_agent_by_id(self, agent_id: str) -> AgentEntity | None:
		"""
		Get an agent by id
		"""
		response = self.db.from_("agents").select("*").eq("id", agent_id).execute()
		if len(response.data) == 0:
			return None
		return AgentEntity(**response.data[0])
	
	def get_agent_by_name(self, agent_name: str) -> AgentEntity | None:
		"""
		Get an agent by name
		"""
		response = (
			self.db.from_("agents").select("*").eq("name", agent_name).execute()
		)
		if len(response.data) == 0:
			return None
		return AgentEntity(**response.data[0])
	
	async def update_agent_by_id(
		self, agent_id: str, agent: AgentUpdatableProperties
	) -> AgentEntity | None:
		"""
		Update an agent by id
		"""
		existed_agent = self.get_agent_by_id(agent_id)
		if existed_agent is None:
			return None
		else:
			client = AsyncOpenAI(api_key=settings.openai_api_key)
			await client.beta.assistants.update(
				assistant_id=agent_id,
				instructions=agent.instructions,
				name=agent.name,
				model=agent.model,
			)
			response = (
				self.db.from_("agents")
				.update(
					{
						"name": agent.name,
						"instructions": agent.instructions,
						"model": agent.model,
					}
				)
				.eq("id", agent_id)
				.execute()
			)
			return AgentEntity(**response.data[0])	
	
	def update_agent_last_update_time(self, agent_id: str):
		"""
		Update the last update time of the agent
		"""
		try:
			self.db.from_("agents").update(
				{"last_update": datetime.now()}).eq("id", agent_id).execute()
		except Exception as e:
			logger.error(e)
	
	async def delete_agent(self, agent_id: str) -> AgentEntity | None:
		"""
		Delete an agent
		"""
		existed_agent = self.get_agent_by_id(agent_id)
		if existed_agent is None:
			return None
		else:
			client = AsyncOpenAI(api_key=settings.openai_api_key)
			await client.beta.assistants.delete(assistant_id=agent_id)
			response = self.db.from_("agents").delete().eq("id", agent_id).execute()
			return AgentEntity(**response.data[0])
	
	

		
