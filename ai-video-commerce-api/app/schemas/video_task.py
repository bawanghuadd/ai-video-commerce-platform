from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


VideoTaskStatus = Literal[
    "待制作",
    "制作中",
    "待审核",
    "已完成",
    "已发布",
    "已驳回",
]


class VideoTaskBase(BaseModel):
    product_id: int = Field(
        gt=0,
        description="关联商品ID",
    )

    script_id: int = Field(
        gt=0,
        description="关联脚本ID",
    )

    title: str = Field(
        min_length=1,
        max_length=200,
        description="视频任务名称",
    )

    platform: str = Field(
        default="抖音",
        min_length=1,
        max_length=30,
    )

    assignee: str = Field(
        default="未分配",
        min_length=1,
        max_length=100,
    )

    status: VideoTaskStatus = "待制作"

    duration_seconds: int = Field(
        default=30,
        ge=1,
        le=3600,
    )

    resolution: str = Field(
        default="1080P",
        min_length=1,
        max_length=30,
    )

    cover_url: str | None = Field(
        default=None,
        max_length=500,
    )

    video_url: str | None = Field(
        default=None,
        max_length=500,
    )

    notes: str | None = Field(
        default=None,
        max_length=5000,
    )

    published_at: datetime | None = None


class VideoTaskCreate(VideoTaskBase):
    pass


class VideoTaskUpdate(BaseModel):
    product_id: int | None = Field(
        default=None,
        gt=0,
    )

    script_id: int | None = Field(
        default=None,
        gt=0,
    )

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )

    platform: str | None = Field(
        default=None,
        min_length=1,
        max_length=30,
    )

    assignee: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    status: VideoTaskStatus | None = None

    duration_seconds: int | None = Field(
        default=None,
        ge=1,
        le=3600,
    )

    resolution: str | None = Field(
        default=None,
        min_length=1,
        max_length=30,
    )

    cover_url: str | None = Field(
        default=None,
        max_length=500,
    )

    video_url: str | None = Field(
        default=None,
        max_length=500,
    )

    notes: str | None = Field(
        default=None,
        max_length=5000,
    )

    published_at: datetime | None = None


class VideoTaskResponse(VideoTaskBase):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    created_at: datetime
    updated_at: datetime