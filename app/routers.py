from fastapi import APIRouter

from app.routes import brain, user

router = APIRouter()
router.include_router(user.router, prefix="", tags=["User"])
router.include_router(brain.router, prefix="", tags=["Brain"])
