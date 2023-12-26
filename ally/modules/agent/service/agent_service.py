

from ally.modules.agent.entity.agent_entity import AgentEntity
from ally.modules.agent.repository.agents import Agents


class AgentService:
  	
	def __init__(self):
		self.agent_repository = Agents()
	
	def create_agent(self, agent) -> AgentEntity:
		return self.agent_repository.create_agent(agent)

	def get_agent_by_id(self, agent_id) -> AgentEntity | None:
		return self.agent_repository.get_agent_by_id(agent_id)
	
	def update_agent_by_id(self, agent_id, agent) -> AgentEntity | None:
		return self.agent_repository.update_agent_by_id(agent_id, agent)
	
	def delete_agent(self, agent_id) -> AgentEntity | None:
		return self.agent_repository.delete_agent(agent_id)
	
	def update_agent_last_update_time(self, agent_id):
		self.agent_repository.update_agent_last_update_time(agent_id)
