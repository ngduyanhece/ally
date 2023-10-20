from fastapi import APIRouter

from app.routes import (api_key, brain, brain_subscription, chat, explore,
                        health, knowledge, meta_brain, notification, prompt,
                        upload, user)

router = APIRouter()
router.include_router(user.router, prefix="", tags=["User"])
router.include_router(brain.router, prefix="", tags=["Brain"])
router.include_router(prompt.router, prefix="", tags=["Prompt"])
router.include_router(api_key.router, prefix="", tags=["API Key"])
router.include_router(upload.router, prefix="", tags=["Upload"])
router.include_router(chat.router, prefix="", tags=["Chat"])
router.include_router(health.router, prefix="", tags=["Health"])
router.include_router(meta_brain.router, prefix="", tags=["Meta Brain"])
router.include_router(explore.router, prefix="", tags=["Explore"])
router.include_router(knowledge.router, prefix="", tags=["Knowledge"])
router.include_router(notification.router, prefix="", tags=["Notification"])
router.include_router(brain_subscription.router, prefix="", tags=["BrainSubscription"])
