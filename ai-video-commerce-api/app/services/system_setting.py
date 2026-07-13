from datetime import datetime

from sqlalchemy.orm import Session

from app.constants.system_settings import DEFAULT_SYSTEM_SETTINGS
from app.models.system_setting import SystemSetting
from app.models.user import User
from app.repositories.system_setting import SystemSettingRepository
from app.schemas.system_setting import SystemSettingResponse, SystemSettingUpdate
from app.services.base import Service, transactional


class SystemSettingService(Service):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.repository = SystemSettingRepository(session)

    def get_settings(self) -> SystemSetting | SystemSettingResponse:
        settings = self.repository.get()
        if settings is not None:
            return settings
        now = datetime.now()
        return SystemSettingResponse(
            id=SystemSettingRepository.SINGLETON_ID,
            **DEFAULT_SYSTEM_SETTINGS,
            updated_by="系统默认",
            created_at=now,
            updated_at=now,
        )

    @transactional("系统设置更新冲突")
    def update_settings(
        self,
        update_data: SystemSettingUpdate,
        current_user: User,
    ) -> SystemSetting:
        settings = self.repository.get()
        if settings is None:
            settings = SystemSetting(
                id=SystemSettingRepository.SINGLETON_ID,
                **DEFAULT_SYSTEM_SETTINGS,
            )
            self.repository.add(settings)
        for field_name, field_value in update_data.model_dump(exclude_unset=True).items():
            setattr(settings, field_name, field_value)
        settings.updated_by = current_user.display_name or current_user.username
        self.repository.flush()
        return settings
