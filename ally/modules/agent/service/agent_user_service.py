from typing import List

from modules.agent.entity.agent_entity import UserAgentEntity
from modules.agent.repository.agents_users import AgentsUsers


class AgentUserService:
	
	def __init__(self):
		self.agent_user_repository = AgentsUsers()
	
	def create_agent_user(self, user_id, agent_id, rights):
		self.agent_user_repository.create_agent_user(
			user_id, agent_id, rights
		)

	def get_user_agents(self, user_id) -> List[UserAgentEntity]:
		return self.agent_user_repository.get_user_agents(user_id)
	
	def get_agent_for_user(self, user_id, agent_id) -> UserAgentEntity | None:
  		return self.agent_user_repository.get_agent_for_user(user_id, agent_id)
