
# from packages.files.processors import filter_file
import modal
from chainlit.context import init_ws_context
from chainlit.element import Element
from chainlit.message import ErrorMessage, Message
from chainlit.server import socket
from chainlit.session import WebsocketSession
from chainlit.telemetry import trace_event
from chainlit.types import UIMessagePayload
from logger import get_logger
from modules.agent.service.agent_service import AgentService
from modules.agent.service.agent_tool_service import AgentToolService
from packages.files.processors import filter_file

logger = get_logger(__name__)


agent_service = AgentService()
agent_tool_service = AgentToolService()

socket.max_http_buffer_size = 2 ** 30  # 1GB


def init_custom_socket():

	@socket.on("delete_agent")
	async def delete_agent(sid):
		if session := WebsocketSession.get(sid):
			trace_event("delete_agent")

			init_ws_context(session)
			agent_name = session.chat_profile
			agent = agent_service.get_agent_by_name(agent_name)
			response = await agent_service.delete_agent(agent.id)
			if response is None:
				await ErrorMessage(author="System", content="Agent not found").send()
				return
			await Message(author="System", content="Agent deleted successfully - Reload your app to see the change").send()
	
	@socket.on("update_tool")
	async def update_tool(sid):
		if session := WebsocketSession.get(sid):
			trace_event("update_tool")

			init_ws_context(session)
			agent_name = session.chat_profile
			agent = agent_service.get_agent_by_name(agent_name)
			response = await agent_tool_service.update_tools_for_agent(agent.id)
			if response is None:
				await ErrorMessage(author="System", content="Agent not found").send()
				return
			await Message(author="System", content="Tools updated successfully for agent {agent_name}".format(agent_name=agent_name)).send()

	@socket.on("update_memory")
	async def update_memory(sid, payload: UIMessagePayload):
		"""Handle a message sent by the User."""
		if session := WebsocketSession.get(sid):
			trace_event("update_memory")
			init_ws_context(session)
			agent_name = session.chat_profile
			files = payload["files"]
			if files:
				file_elements = [Element.from_dict(file) for file in files]
			file_element = file_elements[0]
			logger.info("update_memory")
			logger.info(f"file_element: {file_element}")
			response = await filter_file(file_element, agent_name)
			filter_file_func = modal.Function.lookup("ally", "filter_file_func")
			call = filter_file_func.spawn(file_element, agent_name)
			# message = f"message: {response['message']} - type: {response['type']}"
			await Message(author="System", content=f"upload memory with {file_element.name}").send()
			
