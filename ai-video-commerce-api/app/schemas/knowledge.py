from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


KnowledgeStatus = Literal[
    "草稿",
    "已发布",
    "已归档",
]


class KnowledgeBase(BaseModel):
    product_id: int | None = Field(
        default=None,
        gt=0,
        description="关联商品ID",
    )

    title: str = Field(
        min_length=1,
        max_length=200,
        description="知识标题",
    )

    category: str = Field(
        min_length=1,
        max_length=50,
        description="知识分类",
    )

    summary: str | None = Field(
        default=None,
        max_length=500,
        description="知识摘要",
    )

    content: str = Field(
        min_length=1,
        max_length=30000,
        description="知识正文",
    )

    tags: list[str] = Field(
        default_factory=list,
        max_length=20,
        description="知识标签",
    )

    source_type: str = Field(
        default="手动录入",
        min_length=1,
        max_length=50,
    )

    source_id: int | None = Field(
        default=None,
        gt=0,
    )

    status: KnowledgeStatus = "草稿"

    is_featured: bool = False

    usage_count: int = Field(
        default=0,
        ge=0,
    )

    created_by: str = Field(
        default="系统管理员",
        min_length=1,
        max_length=100,
    )

    @field_validator("tags")
    @classmethod
    def normalize_tags(
        cls,
        value: list[str],
    ) -> list[str]:
        normalized_tags: list[str] = []

        for tag in value:
            cleaned_tag = tag.strip()

            if (
                cleaned_tag
                and cleaned_tag not in normalized_tags
            ):
                normalized_tags.append(cleaned_tag)

        return normalized_tags


class KnowledgeCreate(KnowledgeBase):
    pass


class KnowledgeUpdate(BaseModel):
    product_id: int | None = Field(
        default=None,
        gt=0,
    )

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )

    category: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    summary: str | None = Field(
        default=None,
        max_length=500,
    )

    content: str | None = Field(
        default=None,
        min_length=1,
        max_length=30000,
    )

    tags: list[str] | None = Field(
        default=None,
        max_length=20,
    )

    source_type: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    source_id: int | None = Field(
        default=None,
        gt=0,
    )

    status: KnowledgeStatus | None = None

    is_featured: bool | None = None

    usage_count: int | None = Field(
        default=None,
        ge=0,
    )

    created_by: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    @field_validator("tags")
    @classmethod
    def normalize_tags(
        cls,
        value: list[str] | None,
    ) -> list[str] | None:
        if value is None:
            return None

        normalized_tags: list[str] = []

        for tag in value:
            cleaned_tag = tag.strip()

            if (
                cleaned_tag
                and cleaned_tag not in normalized_tags
            ):
                normalized_tags.append(cleaned_tag)

        return normalized_tags


class KnowledgeResponse(KnowledgeBase):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    created_at: datetime
    updated_at: datetime