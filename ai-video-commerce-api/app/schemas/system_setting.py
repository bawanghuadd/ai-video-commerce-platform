from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


ThemeType = Literal[
    "dark",
    "light",
    "system",
]


class SystemSettingBase(BaseModel):
    platform_name: str = Field(
        min_length=1,
        max_length=100,
    )

    platform_subtitle: str = Field(
        min_length=1,
        max_length=200,
    )

    default_platform: str = Field(
        min_length=1,
        max_length=30,
    )

    timezone: str = Field(
        min_length=1,
        max_length=50,
    )

    theme: ThemeType = "dark"

    ai_provider: str = Field(
        min_length=1,
        max_length=50,
    )

    ai_model: str = Field(
        min_length=1,
        max_length=100,
    )

    temperature: float = Field(
        ge=0,
        le=2,
    )

    enable_ai_generation: bool = True
    enable_auto_review: bool = False
    enable_notifications: bool = True


class SystemSettingUpdate(BaseModel):
    platform_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    platform_subtitle: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )

    default_platform: str | None = Field(
        default=None,
        min_length=1,
        max_length=30,
    )

    timezone: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    theme: ThemeType | None = None

    ai_provider: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    ai_model: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    temperature: float | None = Field(
        default=None,
        ge=0,
        le=2,
    )

    enable_ai_generation: bool | None = None
    enable_auto_review: bool | None = None
    enable_notifications: bool | None = None


class SystemSettingResponse(SystemSettingBase):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    updated_by: str
    created_at: datetime
    updated_at: datetime