
import chainlit as cl
from chainlit.config import config
from chainlit.server import app

from ally.logger import get_logger
from ally.routers import router

logger = get_logger(__name__)

# prevent the chainlit server from opening a browser window

port = 5050

config.run.headless = True
config.run.watch = True
config.run.port = port

@cl.on_message
async def on_message(message: cl.Message):
	await cl.Message(
		content="you have successfully connected to the chainlit server this is a test message your message was: {message}".format(message=message.content),
	).send()

app.include_router(router, prefix="")
