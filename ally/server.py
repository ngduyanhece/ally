
from chainlit.config import config
from chainlit.server import app

from ally.logger import get_logger
from ally.routers import router

logger = get_logger(__name__)

# prevent the chainlit server from opening a browser window

config.run.headless = True
config.run.watch = True

app.include_router(router, prefix="")
