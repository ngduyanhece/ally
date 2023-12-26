
from chainlit.config import config
from chainlit.server import app

from ally.logger import get_logger
from ally.routers import router

logger = get_logger(__name__)

# prevent the chainlit server from opening a browser window

config.run.headless = True
config.run.watch = True
config.run.host = "0.0.0.0"
config.run.port = 5050

app.include_router(router, prefix="")
