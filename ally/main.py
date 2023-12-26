import asyncio

from chainlit.config import DEFAULT_HOST, DEFAULT_PORT

from ally.middlewares.cors import add_cors_middleware
from ally.server import app

if __name__ == "__main__":
  	
	import uvicorn

	add_cors_middleware(app)

	async def start():
		config = uvicorn.Config(
			app,
			host=DEFAULT_HOST,
			port=DEFAULT_PORT,
			ws_per_message_deflate=True,
			workers=6,
		)
		server = uvicorn.Server(config)
		await server.serve()

	asyncio.run(start())
