from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.permissions import require_business_access
from app.schemas.common import ApiResponse
from app.schemas.video_task import VideoTaskCreate, VideoTaskResponse, VideoTaskUpdate
from app.services.video_task import VideoTaskService


router = APIRouter(
    prefix="/api/video-tasks",
    tags=["视频管理"],
    dependencies=[Depends(require_business_access)],
)


def get_video_task_service(db: Session = Depends(get_db)) -> VideoTaskService:
    return VideoTaskService(db)


@router.get("", response_model=ApiResponse[list[VideoTaskResponse]])
def get_video_task_list(
    product_id: int | None = Query(default=None, gt=0),
    script_id: int | None = Query(default=None, gt=0),
    task_status: str | None = Query(default=None, alias="status"),
    keyword: str | None = Query(default=None, max_length=100),
    service: VideoTaskService = Depends(get_video_task_service),
) -> dict:
    return {
        "code": 200,
        "message": "查询视频任务列表成功",
        "data": service.list_tasks(
            product_id=product_id,
            script_id=script_id,
            status=task_status,
            keyword=keyword,
        ),
    }


@router.get("/{video_task_id}", response_model=ApiResponse[VideoTaskResponse])
def get_video_task_detail(
    video_task_id: int,
    service: VideoTaskService = Depends(get_video_task_service),
) -> dict:
    return {"code": 200, "message": "查询视频任务详情成功", "data": service.get_task(video_task_id)}


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ApiResponse[VideoTaskResponse])
def create_video_task(
    create_data: VideoTaskCreate,
    service: VideoTaskService = Depends(get_video_task_service),
) -> dict:
    return {"code": 201, "message": "视频任务创建成功", "data": service.create_task(create_data)}


@router.put("/{video_task_id}", response_model=ApiResponse[VideoTaskResponse])
def update_video_task(
    video_task_id: int,
    update_data: VideoTaskUpdate,
    service: VideoTaskService = Depends(get_video_task_service),
) -> dict:
    return {"code": 200, "message": "视频任务修改成功", "data": service.update_task(video_task_id, update_data)}


@router.delete("/{video_task_id}", response_model=ApiResponse[None])
def delete_video_task(
    video_task_id: int,
    service: VideoTaskService = Depends(get_video_task_service),
) -> dict:
    service.delete_task(video_task_id)
    return {"code": 200, "message": "视频任务删除成功", "data": None}