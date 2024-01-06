

import json

import chainlit as cl
from chainlit.context import context
from chainlit.input_widget import Select
from core.settings import settings
from logger import get_logger
from modules.agent.service.agent_service import AgentService
from modules.chainlit.input_widget import TextInput
from modules.chainlit.utils import (DictToObject, check_files, isAsync,
                                    process_thread_message, upload_files)
from modules.tools.load_tools import _TOOL_NAME_MAP
from openai import AsyncOpenAI

logger = get_logger(__name__)

agent_service = AgentService()

def init_chainlit_chat_process():
	# @cl.author_rename
	# def rename(orig_author: str):
	# 	rename_dict = {"Chatbot": "Assistant"}
	# 	return rename_dict.get(orig_author, orig_author)

	@cl.on_chat_start
	async def setup_conversation():
		openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
		agent_name = cl.user_session.get("chat_profile")
		agent = agent_service.get_agent_by_name(agent_name)
		cl.user_session.set("agent_id", agent.id)
		cl.user_session.set("agent_name", agent_name)

		thread = await openai_client.beta.threads.create()
		cl.user_session.set("thread", thread)
		cl.user_session.set("openai_client", openai_client)

		await cl.Avatar(
        name=agent_name,
        url=agent.icon,
    ).send()

		# setup the actions

		if agent_name != "ally":

			# setup the settings
			agent_settings = await cl.ChatSettings(
				[
					TextInput(
						id="description",
						label="Description",
						initial=agent.description
					),
					TextInput(
						id="instructions",
						label="Instructions",
						initial=agent.instructions,
						multiline=True
					),
					Select(
						id="agent_model",
						label="Agent Model",
						values=["gpt-4-1106-preview", "gpt-3.5-turbo-1106"],
						initial_index=0,
					)
				]
			).send()
	
	@cl.on_message
	async def run_conversation(message_from_ui: cl.Message):
		"""Handle a message sent by the User."""
		agent_name = cl.user_session.get("agent_name")
		thread = cl.user_session.get("thread")
		openai_client = cl.user_session.get("openai_client")
		assistant_id = cl.user_session.get("agent_id")

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
		init_message = await openai_client.beta.threads.messages.create(
			thread_id=thread.id, role="user", content=message_from_ui.content,
			file_ids=file_ids
		)

		# Send empty message to display the loader
		loader_msg = cl.Message(author=agent_name, content="")
		await loader_msg.send()

		# Create the run
		run = await openai_client.beta.threads.runs.create(
			thread_id=thread.id, assistant_id=assistant_id
		)

		message_references = {}
		tool_outputs = []
		# Periodically check for updates
		while True:
			run = await openai_client.beta.threads.runs.retrieve(
				thread_id=thread.id, run_id=run.id
			)

			# Fetch the run steps
			run_steps = await openai_client.beta.threads.runs.steps.list(
				thread_id=thread.id, run_id=run.id, order="asc"
			)
			
			for step in run_steps.data:
				# Fetch step details
				run_step = await openai_client.beta.threads.runs.steps.retrieve(
					thread_id=thread.id, run_id=run.id, step_id=step.id
				)
				step_details = run_step.step_details
				# Update step content in the Chainlit UI
				if step_details.type == "message_creation":
					thread_message = await openai_client.beta.threads.messages.retrieve(
						message_id=step_details.message_creation.message_id,
						thread_id=thread.id,
					)
					await process_thread_message(message_references, thread_message, agent_name)

				if step_details.type == "tool_calls":
					for tool_call in step_details.tool_calls:
						if isinstance(tool_call, dict):
							tool_call = DictToObject(tool_call)
								
						if tool_call.type == "code_interpreter":
							if tool_call.id not in message_references:
								message_references[tool_call.id] = cl.Message(
									author=tool_call.type,
									content=tool_call.code_interpreter.input
									or "# Generating code...",
									language="python",
									parent_id=context.session.root_message.id,
								)
								await message_references[tool_call.id].send()
							else:
								message_references[tool_call.id].content = (
									tool_call.code_interpreter.input
									or "# Generating code..."
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
										
						elif tool_call.type == "function" and run.status == "requires_action":
							function_name = tool_call.function.name
							try:
								function_args = json.loads(tool_call.function.arguments, strict=False)
							except json.JSONDecodeError as e:
								raise ValueError(
										f"Received invalid JSON function arguments: "
										f"{tool_call.function.arguments} for function {tool_call.function.name}"
								) from e

							if tool_call.id not in message_references:
								message_references[tool_call.id] = cl.Message(
									author=function_name,
									content=function_args,
									language="json",
									parent_id=context.session.root_message.id,
								)
								await message_references[tool_call.id].send()
								logger.info("tool arguments: {args}".format(args=tool_call.function.arguments))
								logger.info("function name: {name}".format(name=function_name))
								function = _TOOL_NAME_MAP.get(function_name)
								if isAsync(function):
									logger.info("function is async")
									tool_output = await function(
										**json.loads(tool_call.function.arguments))
								else:
									logger.info("function is not async")
									tool_output = function(
										**json.loads(tool_call.function.arguments))
								tool_outputs.append(
									{"output": tool_output, "tool_call_id": tool_call.id}
								)
				if run.status == "requires_action" and \
					run.required_action.type == "submit_tool_outputs":
					await openai_client.beta.threads.runs.submit_tool_outputs(
						thread_id=thread.id,
						run_id=run.id,
						tool_outputs=tool_outputs,
					)

			await cl.sleep(1)  # Refresh every second
			if run.status in ["cancelled", "failed", "completed", "expired"]:
				break
		
