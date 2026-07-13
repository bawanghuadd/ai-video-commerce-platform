from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.schemas.common import ApiResponse
from app.schemas.content_analysis import (
    ContentAnalysisCreate,
    ContentAnalysisResponse,
    ContentAnalysisUpdate,
)
from app.services.content_analysis import ContentAnalysisService


router = APIRouter(
    prefix="/api/content-analyses",
    tags=["爆款内容拆解"],
    dependencies=[Depends(get_current_user)],
)


def get_content_analysis_service(
    db: Session = Depends(get_db),
) -> ContentAnalysisService:
    return ContentAnalysisService(db)


@router.get("", response_model=ApiResponse[list[ContentAnalysisResponse]])
def get_content_analysis_list(
    product_id: int | None = Query(default=None, gt=0),
    analysis_status: str | None = Query(default=None, alias="status"),
    service: ContentAnalysisService = Depends(get_content_analysis_service),
) -> dict:
    return {
        "code": 200,
        "message": "查询爆款内容拆解列表成功",
        "data": service.list_records(product_id, analysis_status),
    }


@router.get("/{analysis_id}", response_model=ApiResponse[ContentAnalysisResponse])
def get_content_analysis_detail(
    analysis_id: int,
    service: ContentAnalysisService = Depends(get_content_analysis_service),
) -> dict:
    return {
        "code": 200,
        "message": "查询爆款内容拆解详情成功",
        "data": service.get_record(analysis_id),
    }


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiResponse[ContentAnalysisResponse],
)
def create_content_analysis(
    create_data: ContentAnalysisCreate,
    service: ContentAnalysisService = Depends(get_content_analysis_service),
) -> dict:
    return {
        "code": 201,
        "message": "爆款内容拆解记录创建成功",
        "data": service.create_record(create_data),
    }


@router.put(
    "/{analysis_id}",
    response_model=ApiResponse[ContentAnalysisResponse],
)
def update_content_analysis(
    analysis_id: int,
    update_data: ContentAnalysisUpdate,
    service: ContentAnalysisService = Depends(get_content_analysis_service),
) -> dict:
    return {
        "code": 200,
        "message": "爆款内容拆解记录修改成功",
        "data": service.update_record(analysis_id, update_data),
    }


@router.delete("/{analysis_id}", response_model=ApiResponse[None])
def delete_content_analysis(
    analysis_id: int,
    service: ContentAnalysisService = Depends(get_content_analysis_service),
) -> dict:
    service.delete_record(analysis_id)
    return {"code": 200, "message": "爆款内容拆解记录删除成功", "data": None}