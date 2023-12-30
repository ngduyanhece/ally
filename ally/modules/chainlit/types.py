from dataclasses import dataclass
from typing import Optional

from chainlit import AppUser
from chainlit.types import ChatProfile


@dataclass
class AllyAppUser(AppUser):
	id: Optional[str] = None

@dataclass
class AllyChatProfile(ChatProfile):
	"""Specification for a chat profile that can be chosen by the user at the conversation start."""
	agent_id: Optional[str] = None