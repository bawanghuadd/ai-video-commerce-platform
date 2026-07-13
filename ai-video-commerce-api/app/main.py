import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.router import api_router
from app.core.exceptions import AuthenticationError, DomainError
from app.core.logging import request_logging_middleware
from app.database import get_db
from app.init_db import init_db
from app.schemas.common import ApiResponse, ErrorResponse


logger = logging.getLogger("app.error")


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Run only explicitly enabled development bootstrap actions."""

    init_db()
    yield


fastapi_app = FastAPI(
    title="AI短视频电商内容生产与质量管理平台",
    description="基于 Vue3、FastAPI 和 MySQL 的前后端分离项目",
    version="2.0.0",
    lifespan=lifespan,
)

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
fastapi_app.middleware("http")(request_logging_middleware)


@fastapi_app.exception_handler(DomainError)
async def handle_domain_error(_: Request, error: DomainError) -> JSONResponse:
    headers = {"WWW-Authenticate": "Bearer"} if isinstance(error, AuthenticationError) else None
    return JSONResponse(
        status_code=error.status_code,
        content=ErrorResponse(detail=error.message).model_dump(),
        headers=headers,
    )


@fastapi_app.exception_handler(Exception)
async def handle_unexpected_error(_: Request, error: Exception) -> JSONResponse:
    logger.error("unhandled application error type=%s", type(error).__name__)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(detail="服务器内部错误，请稍后重试").model_dump(),
    )


fastapi_app.include_router(api_router)


@fastapi_app.get("/", tags=["系统"], response_model=ApiResponse[None])
def root() -> dict:
    return {"code": 200, "message": "FastAPI 后端运行成功", "data": None}


@fastapi_app.get(
    "/health/live",
    tags=["系统"],
    response_model=ApiResponse[dict[str, str]],
)
def liveness() -> dict:
    return {
        "code": 200,
        "message": "服务存活",
        "data": {"service": "ai-video-commerce-api", "status": "live"},
    }


def probe_database(db: Session) -> None:
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="数据库暂不可用",
        ) from error


@fastapi_app.get(
    "/health/ready",
    tags=["系统"],
    response_model=ApiResponse[dict[str, str]],
)
def readiness(db: Session = Depends(get_db)) -> dict:
    probe_database(db)
    return {
        "code": 200,
        "message": "服务已就绪",
        "data": {"service": "ai-video-commerce-api", "status": "ready"},
    }


@fastapi_app.get(
    "/api/health",
    tags=["系统"],
    response_model=ApiResponse[dict[str, str]],
)
def health_check(db: Session = Depends(get_db)) -> dict:
    """Keep the Phase 1 health path while performing a real readiness probe."""

    probe_database(db)
    return {
        "code": 200,
        "message": "服务正常",
        "data": {
            "service": "ai-video-commerce-api",
            "database": "mysql",
            "status": "running",
        },
    }


app = fastapi_app