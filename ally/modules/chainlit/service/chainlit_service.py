import json

import chainlit as cl
from chainlit.context import context, init_ws_context
from chainlit.message import ErrorMessage
from chainlit.server import socket
from chainlit.session import WebsocketSession
from chainlit.socket import load_user_env, restore_existing_session
from chainlit.telemetry import trace_event
from chainlit.types import UIMessagePayload
from openai import AsyncOpenAI
from sympy import bool_map

from ally.core.settings import settings
from ally.logger import get_logger
from ally.modules.chainlit.service.utils import (DictToObject, check_files,
                                                 process_thread_message,
                                                 upload_files)

logger = get_logger(__name__)

class ChainlitService:
	"""mock agent service"""
	def __init__(self, assistant_id):
		self.client = AsyncOpenAI(api_key=settings.openai_api_key)
		self.assistant_id = assistant_id

	async def _start_chat(self):
		thread = await self.client.beta.threads.create()
		cl.user_session.set("thread", thread)
		await cl.Message(author="assistant", content="").send()
	
	async def _run_conversation(self, message_from_ui: cl.Message):
		thread = cl.user_session.get("thread")
		# Get input files
		input_files = message_from_ui.elements
		
		# Upload files if any and get file_ids
		file_ids = []
		if len(input_files) > 0:

			files_ok = await check_files(input_files)

			if not files_ok:
				file_error_msg = f"Hey, it seems you have uploaded one or more files that we do not support currently, please upload only : {(',').join(allowed_mime)}"
				await cl.Message(content=file_error_msg).send()
				return
			file_ids = await upload_files(input_files)

		# Add the message to the thread with files
		init_message = await self.client.beta.threads.messages.create(
			thread_id=thread.id, role="user", content=message_from_ui.content,
			file_ids=file_ids
		)

		# Send empty message to display the loader
		loader_msg = cl.Message(author="assistant", content="")
		await loader_msg.send()

		# Create the run
		run = await self.client.beta.threads.runs.create(
			thread_id=thread.id, assistant_id=self.assistant_id
		)

		message_references = {}  # type: Dict[str, cl.Message]
		tool_outputs = []
		# Periodically check for updates
		while True:
			run = await self.client.beta.threads.runs.retrieve(
				thread_id=thread.id, run_id=run.id
			)

			# Fetch the run steps
			run_steps = await self.client.beta.threads.runs.steps.list(
				thread_id=thread.id, run_id=run.id, order="asc"
			)
				
			for step in run_steps.data:
				# Fetch step details
				run_step = await self.client.beta.threads.runs.steps.retrieve(
					thread_id=thread.id, run_id=run.id, step_id=step.id
				)
				step_details = run_step.step_details
				# Update step content in the Chainlit UI
				if step_details.type == "message_creation":
					thread_message = await self.client.beta.threads.messages.retrieve(
						message_id=step_details.message_creation.message_id,
						thread_id=thread.id,
					)
					await process_thread_message(message_references, thread_message)

				if step_details.type == "tool_calls":
					for tool_call in step_details.tool_calls:
						if isinstance(tool_call, dict):
							tool_call = DictToObject(tool_call)
											
						if tool_call.type == "code_interpreter":
							if tool_call.id not in message_references:
								message_references[tool_call.id] = cl.Message(
									author=tool_call.type,
									content=tool_call.code_interpreter.input or "# Generating code...",
									language="python",
									parent_id=context.session.root_message.id,
								)
								await message_references[tool_call.id].send()
							else:
								message_references[tool_call.id].content = (
									tool_call.code_interpreter.input or "# Generating code..."
								)
								await message_references[tool_call.id].update()

							tool_output_id = tool_call.id + "output"

							if tool_output_id not in message_references:
								message_references[tool_output_id] = cl.Message(
									author=f"{tool_call.type}_result",
									content=str(tool_call.code_interpreter.outputs) or "",
									language="json",
									parent_id=context.session.root_message.id,
								)
								await message_references[tool_output_id].send()
							else:
								message_references[tool_output_id].content = (
									str(tool_call.code_interpreter.outputs) or ""
								)
								
								await message_references[tool_output_id].update()
									
							tool_outputs.append(
								{
									"output": tool_call.code_interpreter.outputs or "",
									"tool_call_id": tool_call.id,
								}
							)
								
						elif tool_call.type == "retrieval":
							if tool_call.id not in message_references:
								message_references[tool_call.id] = cl.Message(
									author=tool_call.type,
									content="Retrieving information",
									parent_id=context.session.root_message.id,
								)
								await message_references[tool_call.id].send()
										
						elif tool_call.type == "function":
		
							function_name = tool_call.function.name
							function_args = json.loads(tool_call.function.arguments)

							if tool_call.id not in message_references:
								message_references[tool_call.id] = cl.Message(
									author=function_name,
									content=function_args,
									language="json",
									parent_id=context.session.root_message.id,
								)
								await message_references[tool_call.id].send()

								tool_output = bool_map[function_name](
									**json.loads(tool_call.function.arguments))
								tool_outputs.append(
									{"output": tool_output, "tool_call_id": tool_call.id}
								)
					if run.status == "requires_action" and run.required_action.type == "submit_tool_outputs":
						await self.client.beta.threads.runs.submit_tool_outputs(
							thread_id=thread.id,
							run_id=run.id,
							tool_outputs=tool_outputs,
						)
			await cl.sleep(1)  # Refresh every second
			if run.status in ["cancelled", "failed", "completed", "expired"]:
				break

	async def _process_message(
		self, session: WebsocketSession, payload: UIMessagePayload):
		"""Process a message from the user."""
		try:
			context = init_ws_context(session)
			await context.emitter.task_start()
			message = await context.emitter.process_user_message(payload)

			await self._run_conversation(message)
		except InterruptedError:
			pass
		except Exception as e:
			logger.exception(e)
			await ErrorMessage(
				author="Error", content=str(e) or e.__class__.__name__
			).send()
		finally:
			await context.emitter.task_end()
		
	def init_agent_communication(self):

		@socket.on("connect_to_{assistant_id}".format(assistant_id=self.assistant_id))
		async def connect(sid, environ, auth):
			user = None
			token = None
			# Function to send a message to this particular session

			def emit_fn(event, data):
				if session := WebsocketSession.get(sid):
					if session.should_stop:
						session.should_stop = False
						raise InterruptedError("Task stopped by user")
				return socket.emit(event, data, to=sid)

			# Function to ask the user a question
			def ask_user_fn(data, timeout):
				if session := WebsocketSession.get(sid):
					if session.should_stop:
						session.should_stop = False
						raise InterruptedError("Task stopped by user")
				return socket.call("ask", data, timeout=timeout, to=sid)

			session_id = environ.get("HTTP_X_CHAINLIT_SESSION_ID")
			if restore_existing_session(sid, session_id, emit_fn, ask_user_fn):
					return True

			user_env_string = environ.get("HTTP_USER_ENV")
			user_env = load_user_env(user_env_string)
			WebsocketSession(
					id=session_id,
					socket_id=sid,
					emit=emit_fn,
					ask_user=ask_user_fn,
					user_env=user_env,
					user=user,
					token=token,
					chat_profile=environ.get("HTTP_X_CHAINLIT_CHAT_PROFILE"),
			)
			trace_event("connection_successful")
			return True

		@socket.on("connection__to_{assistant_id}_successful")
		async def connection_successful(sid):
			context = init_ws_context(sid)
			if context.session.restored:
				return
			await self._start_chat()

		@socket.on("ui_message_to_{assistant_id}".format(
				assistant_id=self.assistant_id))
		async def message(sid, payload: UIMessagePayload):
			"""Handle a message sent by the User."""
			session = WebsocketSession.require(sid)
			session.should_stop = False
			await self._process_message(session, payload)