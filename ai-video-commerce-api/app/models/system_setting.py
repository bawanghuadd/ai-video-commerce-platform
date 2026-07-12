from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SystemSetting(Base):
    """系统全局设置，项目中只保留一条记录。"""

    __tablename__ = "system_settings"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        default=1,
    )

    platform_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="AI短视频电商平台",
    )

    platform_subtitle: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        default="AI驱动的短视频内容创作与电商增长平台",
    )

    default_platform: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="抖音",
    )

    timezone: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="Asia/Shanghai",
    )

    theme: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="dark",
    )

    ai_provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="OpenAI",
    )

    ai_model: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="default",
    )

    temperature: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.7,
    )

    enable_ai_generation: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    enable_auto_review: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    enable_notifications: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    updated_by: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="系统管理员",
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