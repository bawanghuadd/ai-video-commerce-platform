from sqlalchemy import select

from app.config import settings
from app.database import (
    Base,
    SessionLocal,
    engine,
)

# 导入全部模型，使显式开发建表时 SQLAlchemy 能发现所有表。
from app.models.content_analysis import ContentAnalysis  # noqa: F401
from app.models.knowledge import KnowledgeItem  # noqa: F401
from app.models.product import Product  # noqa: F401
from app.models.script import Script, ScriptScene  # noqa: F401
from app.models.system_setting import SystemSetting
from app.models.user import User
from app.models.video_task import VideoTask  # noqa: F401
from app.security import hash_password


def should_initialize_database() -> bool:
    """仅在显式启用开发初始化能力时访问数据库。"""

    return bool(
        settings.auto_create_schema
        or settings.seed_admin
        or settings.seed_system_settings
    )


def init_db() -> None:
    """按安全开关执行开发建表和种子数据初始化。"""

    if not should_initialize_database():
        return

    if settings.auto_create_schema:
        Base.metadata.create_all(bind=engine)

    if not (settings.seed_admin or settings.seed_system_settings):
        return

    with SessionLocal() as db:
        if settings.seed_admin:
            username = settings.admin_bootstrap_username
            password = settings.admin_bootstrap_password

            admin_user = db.scalar(
                select(User).where(User.username == username)
            )

            if admin_user is None:
                admin_user = User(
                    username=username,
                    display_name="系统管理员",
                    password_hash=hash_password(
                        password.get_secret_value()
                    ),
                    role="admin",
                    is_active=True,
                )
                db.add(admin_user)

        if settings.seed_system_settings:
            system_settings = db.get(SystemSetting, 1)

            if system_settings is None:
                db.add(SystemSetting(id=1))

        db.commit()