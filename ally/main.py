import asyncio

from chainlit.config import DEFAULT_HOST
from middlewares.cors import add_cors_middleware
from server import app, port

add_cors_middleware(app)

if __name__ == "__main__":
  	
	import uvicorn

	add_cors_middleware(app)

	async def start():
		config = uvicorn.Config(
			app,
			host=DEFAULT_HOST,
			port=port,
			ws_per_message_deflate=True,
			workers=6,
		)
		server = uvicorn.Server(config)
		await server.serve()

	asyncio.run(start())
