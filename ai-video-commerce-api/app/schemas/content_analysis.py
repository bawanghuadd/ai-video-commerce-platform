from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ContentAnalysisBase(BaseModel):
    product_id: int = Field(gt=0, description="关联商品ID")
    platform: str = Field(default="抖音", min_length=1, max_length=30)
    content_title: str = Field(min_length=1, max_length=200)
    source_url: str | None = Field(default=None, max_length=500)
    opening_hook: str | None = Field(default=None, max_length=2000)
    content_structure: str | None = Field(default=None, max_length=5000)
    selling_point_expression: str | None = Field(
        default=None,
        max_length=5000,
    )
    target_audience: str | None = Field(default=None, max_length=200)
    analysis_result: str | None = Field(default=None, max_length=5000)
    status: str = Field(default="待拆解", min_length=1, max_length=30)


class ContentAnalysisCreate(ContentAnalysisBase):
    pass


class ContentAnalysisUpdate(BaseModel):
    product_id: int | None = Field(default=None, gt=0)
    platform: str | None = Field(default=None, min_length=1, max_length=30)
    content_title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )
    source_url: str | None = Field(default=None, max_length=500)
    opening_hook: str | None = Field(default=None, max_length=2000)
    content_structure: str | None = Field(default=None, max_length=5000)
    selling_point_expression: str | None = Field(
        default=None,
        max_length=5000,
    )
    target_audience: str | None = Field(default=None, max_length=200)
    analysis_result: str | None = Field(default=None, max_length=5000)
    status: str | None = Field(default=None, min_length=1, max_length=30)


class ContentAnalysisResponse(ContentAnalysisBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime