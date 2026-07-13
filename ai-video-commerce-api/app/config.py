from typing import Literal

from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """读取项目环境配置。"""

    db_host: str = "127.0.0.1"
    db_port: int = 3306
    db_user: str
    db_password: str
    db_name: str

    secret_key: str
    access_token_expire_hours: int = 2

    app_env: Literal["development", "test", "production"] = "development"
    auto_create_schema: bool = False
    seed_admin: bool = False
    seed_system_settings: bool = False
    admin_bootstrap_username: str | None = None
    admin_bootstrap_password: SecretStr | None = None

    @model_validator(mode="after")
    def validate_bootstrap_settings(self):
        unsafe_bootstrap_enabled = (
            self.auto_create_schema
            or self.seed_admin
            or self.seed_system_settings
        )

        if self.app_env == "production" and unsafe_bootstrap_enabled:
            raise ValueError("生产环境禁止自动建表或写入种子数据")

        if self.seed_admin:
            if not self.admin_bootstrap_username:
                raise ValueError("启用管理员种子时必须提供管理员用户名")

            if self.admin_bootstrap_password is None:
                raise ValueError("启用管理员种子时必须提供管理员密码")

            if len(self.admin_bootstrap_password.get_secret_value()) < 12:
                raise ValueError("管理员种子密码不能少于12个字符")

        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()