from typing import List
from uuid import UUID

from ally.core.settings import get_supabase_client
from ally.modules.agent.entity.agent_entity import AgentUser, UserAgentEntity
from ally.modules.agent.repository.interfaces.agents_users_interface import \
    AgentUserInterface


class AgentsUsers(AgentUserInterface):

	def __init__(self):
		supabase_client = get_supabase_client()
		self.db = supabase_client
	
	def get_user_agents(self, user_id) -> List[UserAgentEntity]:
		"""
		get all agents for a user
		"""
		response = (
			self.db.from_("agents_users")
			.select(
				"agent_id, rights, agents (id, name, instructions, model)"
			)
			.filter("user_id", "eq", user_id)
			.execute()
		)
		user_agents: List[UserAgentEntity] = []
		for agent in response.data:
			user_agents.append(
				UserAgentEntity(
					id=agent["agents"]["id"],
					name=agent["agents"]["name"],
					instructions=agent["agents"]["instructions"],
					model=agent["agents"]["model"],
					rights=agent["rights"]
				)
			)
		return user_agents

	def get_agent_for_user(self, user_id, agent_id) -> UserAgentEntity | None:
		"""
		get a specific agent for a user
		"""
		response = (
			self.db.from_("agents_users")
			.select(
				"agent_id, rights, agents (id, name, instructions, model)"
			)
			.filter("user_id", "eq", user_id)
			.filter("agent_id", "eq", agent_id)
			.execute()
		)
		if len(response.data) == 0:
			return None
		agent = response.data[0]
		return UserAgentEntity(
			id=agent["agents"]["id"],
			name=agent["agents"]["name"],
			instructions=agent["agents"]["instructions"],
			model=agent["agents"]["model"],
			rights=agent["rights"]
		)
	
	def delete_agent_user_by_id(self, user_id, agent_id):
		"""
		delete a specific agent for a user
		"""
		response = (
			self.db.from_("agents_users")
			.delete()
			.filter("user_id", "eq", user_id)
			.filter("agent_id", "eq", agent_id)
			.execute()
		)
		return response.data
	
	def delete_agent_users(self, agent_id: str):
		"""
		Delete all users for a agent
		"""
		response = (
			self.db.from_("agents_users")
			.delete()
			.filter("agent_id", "eq", agent_id)
			.execute()
		)
		return response.data
	
	def create_agent_user(
		self,
		user_id: UUID,
		agent_id: str,
		rights
	):
		"""
		Create a agent user
		"""
		response = self.db.from_("agents_users").insert(
			{
				"user_id": str(user_id),
				"agent_id": agent_id,
				"rights": rights,
			}
		).execute()
		return response.data
	
	def get_agent_users(self, agent_id: str) -> List[AgentUser]:
		"""
		Get all users for an agent
		"""
		response = (
			self.db.from_("agents_users")
			.select("*")
			.filter("agent_id", "eq", agent_id)
			.execute()
		)
		agent_users: List[AgentUser] = []
		for agent in response.data:
			agent_users.append(
				AgentUser(
					id=agent["agent_id"],
					user_id=agent["user_id"],
					rights=agent["rights"]
				)
			)
		return agent_users
