from fastapi import APIRouter

from app.routes import api_key, brain, chat, health, prompt, upload, user

router = APIRouter()
router.include_router(user.router, prefix="", tags=["User"])
router.include_router(brain.router, prefix="", tags=["Brain"])
router.include_router(prompt.router, prefix="", tags=["Prompt"])
router.include_router(api_key.router, prefix="", tags=["API Key"])
router.include_router(upload.router, prefix="", tags=["Upload"])
router.include_router(chat.router, prefix="", tags=["Chat"])
router.include_router(health.router, prefix="", tags=["Health"])
