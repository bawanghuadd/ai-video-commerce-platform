from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class VideoTask(Base):
    """视频生产任务。"""

    __tablename__ = "video_tasks"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey(
            "products.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    script_id: Mapped[int] = mapped_column(
        ForeignKey(
            "scripts.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
    )

    platform: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="抖音",
    )

    assignee: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="未分配",
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="待制作",
        index=True,
    )

    duration_seconds: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=30,
    )

    resolution: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="1080P",
    )

    cover_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    video_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    published_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )