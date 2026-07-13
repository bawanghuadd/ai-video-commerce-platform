from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.constants.platforms import Platform
from app.constants.statuses import ContentAnalysisStatus


class ContentAnalysisBase(BaseModel):
    product_id: int = Field(gt=0, description="关联商品ID")
    platform: Platform = "抖音"
    content_title: str = Field(min_length=1, max_length=200)
    source_url: str | None = Field(default=None, max_length=500)
    opening_hook: str | None = Field(default=None, max_length=2000)
    content_structure: str | None = Field(default=None, max_length=5000)
    selling_point_expression: str | None = Field(default=None, max_length=5000)
    target_audience: str | None = Field(default=None, max_length=200)
    analysis_result: str | None = Field(default=None, max_length=5000)
    status: ContentAnalysisStatus = "待拆解"


class ContentAnalysisCreate(ContentAnalysisBase):
    pass


class ContentAnalysisUpdate(BaseModel):
    product_id: int | None = Field(default=None, gt=0)
    platform: Platform | None = None
    content_title: str | None = Field(default=None, min_length=1, max_length=200)
    source_url: str | None = Field(default=None, max_length=500)
    opening_hook: str | None = Field(default=None, max_length=2000)
    content_structure: str | None = Field(default=None, max_length=5000)
    selling_point_expression: str | None = Field(default=None, max_length=5000)
    target_audience: str | None = Field(default=None, max_length=200)
    analysis_result: str | None = Field(default=None, max_length=5000)
    status: ContentAnalysisStatus | None = None


class ContentAnalysisResponse(ContentAnalysisBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime