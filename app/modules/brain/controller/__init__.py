from fastapi import APIRouter

from app.modules.prompt.service.prompt_service import PromptService

prompt_router = APIRouter()

promptService = PromptService()