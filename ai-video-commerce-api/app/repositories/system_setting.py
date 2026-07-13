from sqlalchemy.orm import Session

from app.models.system_setting import SystemSetting


class SystemSettingRepository:
    SINGLETON_ID = 1

    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self) -> SystemSetting | None:
        return self.session.get(SystemSetting, self.SINGLETON_ID)

    def add(self, settings: SystemSetting) -> None:
        self.session.add(settings)

    def flush(self) -> None:
        self.session.flush()
