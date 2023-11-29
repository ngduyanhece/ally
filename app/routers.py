from fastapi import APIRouter

from app.modules.agent.controller import agent_routes
from app.modules.api_key.controller import api_key_routes
from app.modules.brain.controller import brain_routes, runtime_routes
from app.modules.chat.controller import chat_routes
from app.modules.knowledge.controller import knowledge_routes
from app.modules.notification.controller import notification_routes
from app.modules.prompt.controller import prompt_routes
from app.modules.user.controller import user_routes

router = APIRouter()
router.include_router(api_key_routes.api_key_router, tags=["API Key"])
router.include_router(user_routes.user_router, tags=["User"])
router.include_router(prompt_routes.prompt_router, tags=["Prompt"])
router.include_router(brain_routes.brain_router, tags=["Brain"])
router.include_router(runtime_routes.runtime_router, tags=["Runtime"])
router.include_router(chat_routes.chat_router, tags=["Chat"])
router.include_router(agent_routes.agent_router, tags=["Agent"])
router.include_router(notification_routes.notification_router, 
                      tags=["Notification"])
router.include_router(knowledge_routes.knowledge_router, tags=["Knowledge"])
