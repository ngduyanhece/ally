
from typing import List, Optional, Union
from uuid import UUID

from fastapi import Depends, HTTPException, status

from ally.middlewares.auth.auth_bearer import get_current_user
from ally.modules.agent.entity.agent_entity import RoleEnum
from ally.modules.agent.service.agent_service import AgentService
from ally.modules.agent.service.agent_user_service import AgentUserService
from ally.modules.user.entity.user_identity import UserIdentity

agent_service = AgentService()
agent_user_service = AgentUserService()

def has_agent_authorization(
	required_roles: Optional[Union[RoleEnum, List[RoleEnum]]] = RoleEnum.Owner
):
	"""
	Decorator to check if the user has the required role(s) for the agent
	param: required_roles: The role(s) required to access the agent
	return: A wrapper function that checks the authorization
	"""

	async def wrapper(
		agent_id: str, current_user: UserIdentity = Depends(get_current_user)
	):
		nonlocal required_roles
		if isinstance(required_roles, str):
			required_roles = [required_roles]  # Convert single role to a list
		validate_agent_authorization(
			agent_id=agent_id, user_id=current_user.id, required_roles=required_roles
		)

	return wrapper


def validate_agent_authorization(
	agent_id: str,
	user_id: UUID,
	required_roles: Optional[Union[RoleEnum, List[RoleEnum]]] = RoleEnum.Owner,
):
	"""
	Function to check if the user has the required role(s) for the agent
	param: agent_id: The id of the agent
	param: user_id: The id of the user
	param: required_roles: The role(s) required to access the agent
	return: None
	"""

	if required_roles is None:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Missing required role",
		)

	user_agent = agent_user_service.get_agent_for_user(user_id, agent_id)
	if user_agent is None:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail="You don't have permission for this agent",
		)

	# Convert single role to a list to handle both cases
	if isinstance(required_roles, str):
			required_roles = [required_roles]

	# Check if the user has at least one of the required roles
	if user_agent.rights not in required_roles:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail="You don't have the required role(s) for this agent",
		)
