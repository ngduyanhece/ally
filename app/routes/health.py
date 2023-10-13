from fastapi import APIRouter

router = APIRouter()

@router.get("/upload/healthz")
async def upload_healthz():
    return {"status": "ok"}

@router.get("/chat/healthz")
async def chat_healthz():
    return {"status": "ok"}
