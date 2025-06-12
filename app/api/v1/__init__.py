from fastapi import APIRouter
from core.config import settings

from .golf_assistant import router as golf_assistant_router


api_router = APIRouter(prefix=settings.API_V1_STR)
api_router.include_router(golf_assistant_router)
