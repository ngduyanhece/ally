from fastapi import APIRouter

from ally.modules.agent.controller import agent_routes
from ally.modules.api_key.controller import api_key_routes
from ally.modules.chainlit.controller import chainlit_routes
from ally.modules.user.controller import user_routes

router = APIRouter()
router.include_router(api_key_routes.api_key_router, tags=["API Key"])
router.include_router(user_routes.user_router, tags=["User"])
router.include_router(agent_routes.agent_router, tags=["Agent"])
router.include_router(chainlit_routes.chat_router, tags=["Chat"])
