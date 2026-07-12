from app.api.products import router as products_router
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.init_db import init_db
from app.api.content_analysis import router as content_analysis_router
from app.api.scripts import router as scripts_router
from app.api.video_tasks import router as video_tasks_router
from app.api.knowledge import router as knowledge_router
from app.api.system_settings import (
    router as system_settings_router,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """启动时创建数据表并初始化管理员。"""
    init_db()
    yield


fastapi_app = FastAPI(
    title="AI短视频电商内容生产与质量管理平台",
    description="基于 Vue3、FastAPI 和 MySQL 的前后端分离项目",
    version="1.0.0",
    lifespan=lifespan,
)

fastapi_app.include_router(products_router)
fastapi_app.include_router(auth_router)
fastapi_app.include_router(content_analysis_router)
fastapi_app.include_router(scripts_router)
fastapi_app.include_router(video_tasks_router)
fastapi_app.include_router(knowledge_router)
fastapi_app.include_router(
    system_settings_router
)




@fastapi_app.get("/", tags=["系统"])
def root() -> dict:
    return {
        "code": 200,
        "message": "FastAPI 后端运行成功",
        "data": None,
    }


@fastapi_app.get("/api/health", tags=["系统"])
def health_check() -> dict:
    return {
        "code": 200,
        "message": "服务正常",
        "data": {
            "service": "ai-video-commerce-api",
            "database": "mysql",
            "status": "running",
        },
    }


# 包裹整个 FastAPI 应用，保证异常响应也包含 CORS 头
app = CORSMiddleware(
    app=fastapi_app,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)