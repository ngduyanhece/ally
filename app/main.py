from fastapi import FastAPI

from app.middlewares.cors import add_cors_middleware
from app.routers import router

app = FastAPI()
add_cors_middleware(app)
app.include_router(router, prefix="/api/v1")


if __name__ == "__main__":
    # run main.py to debug backend
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5050)
