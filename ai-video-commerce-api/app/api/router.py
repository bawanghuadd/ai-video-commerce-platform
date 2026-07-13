from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.content_analysis import router as content_analysis_router
from app.api.knowledge import router as knowledge_router
from app.api.products import router as products_router
from app.api.scripts import router as scripts_router
from app.api.system_settings import router as system_settings_router
from app.api.video_tasks import router as video_tasks_router


api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(products_router)
api_router.include_router(content_analysis_router)
api_router.include_router(scripts_router)
api_router.include_router(video_tasks_router)
api_router.include_router(knowledge_router)
api_router.include_router(system_settings_router)
