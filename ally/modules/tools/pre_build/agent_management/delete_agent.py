from ally.modules.agent.service.agent_service import AgentService


async def delete_agent_tool(name: str):
  """delete agent in Ally Platform"""
  response = await AgentService.delete_agent(agent_id)
	if response is None:
		raise HTTPException(status_code=404, detail="Agent not found")
	return response