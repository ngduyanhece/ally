
from typing import List

import chainlit as cl
from logger import get_logger
from modules.agent.service.agent_user_service import AgentUserService
from modules.chainlit.types import AllyChatProfile

agent_user_service = AgentUserService()
logger = get_logger(__name__)

def init_chainlit_chat_profile():
	@cl.set_chat_profiles
	async def chat_profile(current_user: cl.AppUser):
		logger.info("current user: {}".format(current_user))
		agents = agent_user_service.get_user_agents(current_user.tags[0])
		user_chat_profiles: List[AllyChatProfile] = []
		for agent in agents:
			user_chat_profiles.append(
				cl.ChatProfile(
					name=agent.name,
					markdown_description=agent.description,
					icon=agent.icon,
				)
			)
		return user_chat_profiles
		
