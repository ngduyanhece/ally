

from chainlit import config
from chainlit.server import app
from logger import get_logger
from modules.chainlit.actions import init_chainlit_actions
from modules.chainlit.chat_process import init_chainlit_chat_process
from modules.chainlit.chat_profiles import init_chainlit_chat_profile
from modules.chainlit.chat_settings import init_chainlit_settings
from modules.chainlit.password_auth import init_chainlit_password_auth
from modules.chainlit.socket import init_custom_socket
from routers import router
from starlette.middleware.cors import CORSMiddleware

logger = get_logger(__name__)

# prevent the chainlit server from opening a browser window

port = 5050

config.run.headless = True
config.run.watch = True
config.run.port = port

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)


init_custom_socket()
init_chainlit_chat_profile()
init_chainlit_password_auth()
init_chainlit_actions()
init_chainlit_chat_process()
init_chainlit_settings()

app.include_router(router, prefix="")