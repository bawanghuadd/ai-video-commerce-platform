from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product
from app.models.script import Script
from app.models.video_task import VideoTask
from app.schemas.video_task import (
    VideoTaskCreate,
    VideoTaskResponse,
    VideoTaskUpdate,
)
from app.security import get_current_user


router = APIRouter(
    prefix="/api/video-tasks",
    tags=["视频管理"],
    dependencies=[
        Depends(get_current_user),
    ],
)


def get_video_task_or_404(
    video_task_id: int,
    db: Session,
) -> VideoTask:
    """获取视频任务，不存在时返回404。"""

    video_task = db.get(
        VideoTask,
        video_task_id,
    )

    if video_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="视频任务不存在",
        )

    return video_task


def validate_references(
    db: Session,
    product_id: int,
    script_id: int,
) -> None:
    """校验商品和脚本是否存在且相互匹配。"""

    product = db.get(
        Product,
        product_id,
    )

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="关联商品不存在",
        )

    script = db.get(
        Script,
        script_id,
    )

    if script is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="关联脚本不存在",
        )

    if script.product_id != product_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="所选脚本与商品不一致",
        )


@router.get("")
def get_video_task_list(
    product_id: int | None = Query(
        default=None,
        gt=0,
    ),
    script_id: int | None = Query(
        default=None,
        gt=0,
    ),
    task_status: str | None = Query(
        default=None,
        alias="status",
    ),
    keyword: str | None = Query(
        default=None,
        max_length=100,
    ),
    db: Session = Depends(get_db),
) -> dict:
    """查询视频任务列表。"""

    statement = select(VideoTask)

    if product_id is not None:
        statement = statement.where(
            VideoTask.product_id == product_id
        )

    if script_id is not None:
        statement = statement.where(
            VideoTask.script_id == script_id
        )

    if task_status:
        statement = statement.where(
            VideoTask.status == task_status
        )

    if keyword:
        search_keyword = (
            f"%{keyword.strip()}%"
        )

        statement = statement.where(
            or_(
                VideoTask.title.like(
                    search_keyword
                ),
                VideoTask.assignee.like(
                    search_keyword
                ),
            )
        )

    statement = statement.order_by(
        VideoTask.updated_at.desc(),
        VideoTask.id.desc(),
    )

    video_tasks = db.scalars(
        statement
    ).all()

    return {
        "code": 200,
        "message": "查询视频任务列表成功",
        "data": [
            VideoTaskResponse
            .model_validate(video_task)
            .model_dump()
            for video_task in video_tasks
        ],
    }


@router.get("/{video_task_id}")
def get_video_task_detail(
    video_task_id: int,
    db: Session = Depends(get_db),
) -> dict:
    """查询视频任务详情。"""

    video_task = get_video_task_or_404(
        video_task_id,
        db,
    )

    return {
        "code": 200,
        "message": "查询视频任务详情成功",
        "data": VideoTaskResponse
        .model_validate(video_task)
        .model_dump(),
    }


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
def create_video_task(
    create_data: VideoTaskCreate,
    db: Session = Depends(get_db),
) -> dict:
    """创建视频生产任务。"""

    validate_references(
        db=db,
        product_id=create_data.product_id,
        script_id=create_data.script_id,
    )

    video_task = VideoTask(
        **create_data.model_dump()
    )

    db.add(video_task)
    db.commit()
    db.refresh(video_task)

    return {
        "code": 201,
        "message": "视频任务创建成功",
        "data": VideoTaskResponse
        .model_validate(video_task)
        .model_dump(),
    }


@router.put("/{video_task_id}")
def update_video_task(
    video_task_id: int,
    update_data: VideoTaskUpdate,
    db: Session = Depends(get_db),
) -> dict:
    """修改视频生产任务。"""

    video_task = get_video_task_or_404(
        video_task_id,
        db,
    )

    update_fields = update_data.model_dump(
        exclude_unset=True,
    )

    final_product_id = update_fields.get(
        "product_id",
        video_task.product_id,
    )

    final_script_id = update_fields.get(
        "script_id",
        video_task.script_id,
    )

    validate_references(
        db=db,
        product_id=final_product_id,
        script_id=final_script_id,
    )

    for field_name, field_value in update_fields.items():
        setattr(
            video_task,
            field_name,
            field_value,
        )

    db.commit()
    db.refresh(video_task)

    return {
        "code": 200,
        "message": "视频任务修改成功",
        "data": VideoTaskResponse
        .model_validate(video_task)
        .model_dump(),
    }


@router.delete("/{video_task_id}")
def delete_video_task(
    video_task_id: int,
    db: Session = Depends(get_db),
) -> dict:
    """删除视频生产任务。"""

    video_task = get_video_task_or_404(
        video_task_id,
        db,
    )

    db.delete(video_task)
    db.commit()

    return {
        "code": 200,
        "message": "视频任务删除成功",
        "data": None,
    }