from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def root():
    """
    Root endpoint to check the status of the API.
    """
    return {"status": "OK"}


@router.get("/healthz", tags=["Health"])
async def healthz():
    return {"status": "ok"}
