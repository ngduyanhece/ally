
from typing import List

import chainlit as cl

from ally.logger import get_logger
from ally.modules.agent.service.agent_user_service import AgentUserService
from ally.modules.chainlit.types import AllyChatProfile

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
					markdown_description="",
					icon="https://myfirefly-ai.s3.amazonaws.com/ally_agent_avatar/3.png"
				)
			)
		return user_chat_profiles
		
