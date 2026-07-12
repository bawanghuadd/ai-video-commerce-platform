from sqlalchemy import select

from app.database import (
    Base,
    SessionLocal,
    engine,
)

# 导入全部模型，使 SQLAlchemy 能发现所有表。
from app.models.content_analysis import ContentAnalysis  # noqa: F401
from app.models.knowledge import KnowledgeItem  # noqa: F401
from app.models.product import Product  # noqa: F401
from app.models.script import Script, ScriptScene  # noqa: F401
from app.models.system_setting import SystemSetting
from app.models.user import User
from app.models.video_task import VideoTask  # noqa: F401
from app.security import hash_password


def init_db() -> None:
    """创建数据表并初始化系统基础数据。"""

    Base.metadata.create_all(
        bind=engine,
    )

    with SessionLocal() as db:
        admin_user = db.scalar(
            select(User).where(
                User.username == "admin"
            )
        )

        if admin_user is None:
            admin_user = User(
                username="admin",
                display_name="系统管理员",
                password_hash=hash_password(
                    "123456"
                ),
                role="admin",
                is_active=True,
            )

            db.add(admin_user)

            print("管理员账号创建成功")
        else:
            print("管理员账号已经存在")

        system_settings = db.get(
            SystemSetting,
            1,
        )

        if system_settings is None:
            system_settings = SystemSetting(
                id=1,
                platform_name="AI短视频电商平台",
                platform_subtitle=(
                    "AI驱动的短视频内容创作与电商增长平台"
                ),
                default_platform="抖音",
                timezone="Asia/Shanghai",
                theme="dark",
                ai_provider="OpenAI",
                ai_model="default",
                temperature=0.7,
                enable_ai_generation=True,
                enable_auto_review=False,
                enable_notifications=True,
                updated_by="系统管理员",
            )

            db.add(system_settings)

            print("默认系统设置创建成功")
        else:
            print("系统设置已经存在")

        db.commit()