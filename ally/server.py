

from chainlit import config
from chainlit.server import app

from ally.logger import get_logger
from ally.modules.chainlit.actions import init_chainlit_actions
from ally.modules.chainlit.chat_process import init_chainlit_chat_process
from ally.modules.chainlit.chat_profiles import init_chainlit_chat_profile
from ally.modules.chainlit.chat_settings import init_chainlit_settings
from ally.modules.chainlit.password_auth import init_chainlit_password_auth
from ally.routers import router

logger = get_logger(__name__)

# prevent the chainlit server from opening a browser window

port = 5050

config.run.headless = True
config.run.watch = True
config.run.port = port

init_chainlit_chat_profile()
init_chainlit_password_auth()
init_chainlit_actions()
init_chainlit_chat_process()
init_chainlit_settings()

app.include_router(router, prefix="")