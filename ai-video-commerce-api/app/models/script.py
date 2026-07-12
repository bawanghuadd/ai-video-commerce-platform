from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Script(Base):
    """短视频脚本。"""

    __tablename__ = "scripts"

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

    content_analysis_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "content_analyses.id",
            ondelete="SET NULL",
        ),
        nullable=True,
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

    script_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="带货短视频",
    )

    opening_hook: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    full_script: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    duration_seconds: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=30,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="草稿",
        index=True,
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

    scenes: Mapped[list["ScriptScene"]] = relationship(
        back_populates="script",
        cascade="all, delete-orphan",
        order_by="ScriptScene.scene_number",
        lazy="selectin",
    )


class ScriptScene(Base):
    """脚本中的单个分镜。"""

    __tablename__ = "script_scenes"

    __table_args__ = (
        UniqueConstraint(
            "script_id",
            "scene_number",
            name="uq_script_scene_number",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
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

    scene_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    duration_seconds: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=5,
    )

    shot_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    visual_content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    voiceover: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    subtitle: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    camera_movement: Mapped[str | None] = mapped_column(
        String(200),
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

    script: Mapped["Script"] = relationship(
        back_populates="scenes",
    )