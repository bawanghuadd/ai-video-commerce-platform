from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.schemas.common import ApiResponse
from app.schemas.system_setting import SystemSettingResponse, SystemSettingUpdate
from app.services.system_setting import SystemSettingService


router = APIRouter(prefix="/api/system-settings", tags=["系统设置"])


def get_system_setting_service(
    db: Session = Depends(get_db),
) -> SystemSettingService:
    return SystemSettingService(db)


@router.get("", response_model=ApiResponse[SystemSettingResponse])
def get_system_settings(
    current_user=Depends(get_current_user),
    service: SystemSettingService = Depends(get_system_setting_service),
) -> dict:
    del current_user
    return {
        "code": 200,
        "message": "获取系统设置成功",
        "data": service.get_settings(),
    }


@router.put("", response_model=ApiResponse[SystemSettingResponse])
def update_system_settings(
    update_data: SystemSettingUpdate,
    current_user=Depends(get_current_user),
    service: SystemSettingService = Depends(get_system_setting_service),
) -> dict:
    return {
        "code": 200,
        "message": "系统设置保存成功",
        "data": service.update_settings(update_data, current_user),
    }