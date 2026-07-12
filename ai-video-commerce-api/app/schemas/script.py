from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


ScriptStatus = Literal[
    "草稿",
    "待审核",
    "已通过",
    "已驳回",
]


class ScriptSceneBase(BaseModel):
    scene_number: int = Field(
        ge=1,
        description="分镜序号",
    )

    duration_seconds: int = Field(
        default=5,
        ge=1,
        le=600,
        description="分镜时长，单位为秒",
    )

    shot_type: str | None = Field(
        default=None,
        max_length=50,
        description="景别",
    )

    visual_content: str = Field(
        min_length=1,
        max_length=5000,
        description="画面内容",
    )

    voiceover: str | None = Field(
        default=None,
        max_length=5000,
        description="口播或旁白",
    )

    subtitle: str | None = Field(
        default=None,
        max_length=2000,
        description="字幕",
    )

    camera_movement: str | None = Field(
        default=None,
        max_length=200,
        description="运镜方式",
    )


class ScriptSceneCreate(ScriptSceneBase):
    pass


class ScriptSceneResponse(ScriptSceneBase):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    script_id: int
    created_at: datetime
    updated_at: datetime


class ScriptBase(BaseModel):
    product_id: int = Field(
        gt=0,
        description="关联商品ID",
    )

    content_analysis_id: int | None = Field(
        default=None,
        gt=0,
        description="关联爆款拆解记录ID",
    )

    title: str = Field(
        min_length=1,
        max_length=200,
        description="脚本标题",
    )

    platform: str = Field(
        default="抖音",
        min_length=1,
        max_length=30,
    )

    script_type: str = Field(
        default="带货短视频",
        min_length=1,
        max_length=50,
    )

    opening_hook: str | None = Field(
        default=None,
        max_length=5000,
    )

    full_script: str | None = Field(
        default=None,
        max_length=20000,
    )

    duration_seconds: int = Field(
        default=30,
        ge=1,
        le=3600,
    )

    status: ScriptStatus = "草稿"


class ScriptCreate(ScriptBase):
    scenes: list[ScriptSceneCreate] = Field(
        default_factory=list,
    )

    @model_validator(mode="after")
    def validate_scene_numbers(self):
        scene_numbers = [
            scene.scene_number
            for scene in self.scenes
        ]

        if len(scene_numbers) != len(set(scene_numbers)):
            raise ValueError(
                "同一脚本中的分镜序号不能重复"
            )

        return self


class ScriptUpdate(BaseModel):
    product_id: int | None = Field(
        default=None,
        gt=0,
    )

    content_analysis_id: int | None = Field(
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

    script_type: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    opening_hook: str | None = Field(
        default=None,
        max_length=5000,
    )

    full_script: str | None = Field(
        default=None,
        max_length=20000,
    )

    duration_seconds: int | None = Field(
        default=None,
        ge=1,
        le=3600,
    )

    status: ScriptStatus | None = None

    scenes: list[ScriptSceneCreate] | None = None

    @model_validator(mode="after")
    def validate_scene_numbers(self):
        if self.scenes is None:
            return self

        scene_numbers = [
            scene.scene_number
            for scene in self.scenes
        ]

        if len(scene_numbers) != len(set(scene_numbers)):
            raise ValueError(
                "同一脚本中的分镜序号不能重复"
            )

        return self


class ScriptResponse(ScriptBase):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    created_at: datetime
    updated_at: datetime
    scenes: list[ScriptSceneResponse] = Field(
        default_factory=list,
    )