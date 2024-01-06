import asyncio
from typing import Dict

import chainlit as cl
from core.settings import settings
from openai import AsyncOpenAI
from openai.types.beta.threads import (MessageContentImageFile,
                                       MessageContentText, ThreadMessage)

client = AsyncOpenAI(api_key=settings.openai_api_key)

def isAsync(someFunc):
	return asyncio.iscoroutinefunction(someFunc)

# List of allowed mime types
allowed_mime = ['text/csv', 'application/pdf']

# Check if the files uploaded are allowed
async def check_files(files):
	# for file in files:
	# 	if file.mime not in allowed_mime:
	# 		return False
	return True


# Upload files to the assistant
async def upload_files(files):
	file_ids = []
	for file in files:
		uploaded_file = await client.files.create(
			file=file.content, purpose="assistants")
		file_ids.append(uploaded_file.id)
	return file_ids

async def process_thread_message(
		message_references: Dict[str, cl.Message], thread_message: ThreadMessage, author: str
):
	for idx, content_message in enumerate(thread_message.content):
		id = thread_message.id + str(idx)
		if isinstance(content_message, MessageContentText):
			if id in message_references:
				msg = message_references[id]
				msg.content = content_message.text.value
				await msg.update()
			else:
				message_references[id] = cl.Message(
					author=author, content=content_message.text.value
				)
				await message_references[id].send()
		elif isinstance(content_message, MessageContentImageFile):
			image_id = content_message.image_file.file_id
			response = await client.files.with_raw_response.content(image_id)
			elements = [
				cl.Image(
					name=image_id,
					content=response.content,
					display="inline",
					size="large",
				),
			]

			if id not in message_references:
				message_references[id] = cl.Message(
					author=author,
					content="",
					elements=elements,
				)
				await message_references[id].send()
		else:
			print("unknown message type", type(content_message))

class DictToObject:
	def __init__(self, dictionary):
		for key, value in dictionary.items():
			if isinstance(value, dict):
				setattr(self, key, DictToObject(value))
			else:
				setattr(self, key, value)
							
	def __str__(self):
		return '\n'.join(f'{key}: {value}' for key, value in self.__dict__.items())
