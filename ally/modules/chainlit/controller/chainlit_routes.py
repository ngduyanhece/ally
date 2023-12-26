

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from ally.logger import get_logger
from ally.middlewares.auth.auth_bearer import AuthBearer
from ally.modules.chainlit.service.chainlit_service import ChainlitService
from ally.modules.chainlit.service.ui_template import get_html_template

logger = get_logger(__name__)
chat_router = APIRouter()

@chat_router.post("/connect/{agent_id}", dependencies=[Depends(AuthBearer())])
async def setup_chainlit_agent(
	agent_id: str,
):
	"""
	setup all the necessary components for a chainlit agent
	"""
	chainlit_service = ChainlitService(agent_id)
	chainlit_service.init_agent_communication()
	return {"message": "communication for agent {agent_id} initialized successfully".format(agent_id=agent_id)}

@chat_router.get(
	"/connect/{agent_id}/start"
)
async def serve(
	agent_id: str,
	request: Request
):
	"""
	start a new chat session
	"""
	html_template = get_html_template()
	"""Serve the UI files."""
	response = HTMLResponse(content=html_template, status_code=200)
	return response