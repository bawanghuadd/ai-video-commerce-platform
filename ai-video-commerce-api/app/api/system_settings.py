from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.system_setting import SystemSetting
from app.models.user import User
from app.schemas.system_setting import (
    SystemSettingResponse,
    SystemSettingUpdate,
)
from app.security import get_current_user


router = APIRouter(
    prefix="/api/system-settings",
    tags=["系统设置"],
)


def get_or_create_settings(
    db: Session,
) -> SystemSetting:
    settings = db.get(
        SystemSetting,
        1,
    )

    if settings is not None:
        return settings

    settings = SystemSetting(
        id=1,
    )

    db.add(settings)
    db.commit()
    db.refresh(settings)

    return settings


@router.get("")
def get_system_settings(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> dict:
    """获取系统全局配置。"""

    settings = get_or_create_settings(db)

    return {
        "code": 200,
        "message": "获取系统设置成功",
        "data": (
            SystemSettingResponse
            .model_validate(settings)
            .model_dump()
        ),
    }


@router.put("")
def update_system_settings(
    update_data: SystemSettingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
) -> dict:
    """修改系统全局配置。"""

    settings = get_or_create_settings(db)

    update_fields = update_data.model_dump(
        exclude_unset=True,
    )

    for field_name, field_value in update_fields.items():
        setattr(
            settings,
            field_name,
            field_value,
        )

    settings.updated_by = (
        current_user.display_name
        or current_user.username
    )

    db.commit()
    db.refresh(settings)

    return {
        "code": 200,
        "message": "系统设置保存成功",
        "data": (
            SystemSettingResponse
            .model_validate(settings)
            .model_dump()
        ),
    }
