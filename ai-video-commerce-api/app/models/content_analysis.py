from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ContentAnalysis(Base):
    """爆款内容拆解记录。"""

    __tablename__ = "content_analyses"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
    )

    # 关联商品表
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    platform: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="抖音",
    )

    content_title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    source_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    opening_hook: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    content_structure: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    selling_point_expression: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    target_audience: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    analysis_result: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="待拆解",
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