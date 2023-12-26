
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from ally.logger import get_logger
from ally.middlewares.auth.auth_bearer import AuthBearer, get_current_user
from ally.modules.agent.dto.inputs import (AgentUpdatableProperties,
                                           CreateAgentProperties)
from ally.modules.agent.entity.agent_entity import (AgentEntity, RoleEnum,
                                                    UserAgentEntity)
from ally.modules.agent.service.agent_authorization_service import \
    has_agent_authorization
from ally.modules.agent.service.agent_service import AgentService
from ally.modules.agent.service.agent_user_service import AgentUserService
from ally.modules.user.entity.user_identity import UserIdentity

logger = get_logger(__name__)
agent_router = APIRouter()

agent_service = AgentService()
agent_user_service = AgentUserService()

@agent_router.post("/agents/", dependencies=[Depends(AuthBearer())])
async def create_new_agent(
	agent: CreateAgentProperties,
	current_user: UserIdentity = Depends(get_current_user)
):
	""" Create a new agent for user"""
	new_agent = await agent_service.create_agent(agent)
	agent_user_service.create_agent_user(
		current_user.id, new_agent.id, RoleEnum.Owner
	)
	return {"id": new_agent.id, "name": new_agent.name, "rights": "Owner"}

@agent_router.get("/agents/", dependencies=[Depends(AuthBearer())])
async def get_agents(
	current_user: UserIdentity = Depends(get_current_user)
) -> List[UserAgentEntity]:
	""" Get all agents for user"""
	return agent_user_service.get_user_agents(current_user.id)

@agent_router.get(
	"/agents/{agent_id}",
	dependencies=[
		Depends(AuthBearer()),
		Depends(
			has_agent_authorization(
				required_roles=[RoleEnum.Owner, RoleEnum.Editor, RoleEnum.Viewer]
			)
		),
	],
)
async def get_agent(
	agent_id: str,
) -> AgentEntity | None:
	""" Get a specific agent for user"""
	agent = agent_service.get_agent_by_id(agent_id)
	if agent is None:
		raise HTTPException(status_code=404, detail="Agent not found")
	return agent

@agent_router.put(
	"/agents/{agent_id}",
	dependencies=[
		Depends(AuthBearer()),
		Depends(
			has_agent_authorization(
				required_roles=[RoleEnum.Owner, RoleEnum.Editor]
			)
		),
	],
)
async def update_agent(
	agent_id: str,
	agent: AgentUpdatableProperties,
) -> AgentEntity | None:
	""" Update a specific agent for user"""
	response = await agent_service.update_agent_by_id(agent_id, agent)
	if response is None:
		raise HTTPException(status_code=404, detail="Agent not found")
	agent_service.update_agent_last_update_time(agent_id)
	return response

@agent_router.delete(
	"/agents/{agent_id}",
	dependencies=[
		Depends(AuthBearer()),
		Depends(
			has_agent_authorization(
				required_roles=[RoleEnum.Owner]
			)
		),
	],
)
async def delete_agent(
	agent_id: str,
) -> AgentEntity | None:
	""" Delete a specific agent for user"""
	response = await agent_service.delete_agent(agent_id)
	if response is None:
		raise HTTPException(status_code=404, detail="Agent not found")
	return response
