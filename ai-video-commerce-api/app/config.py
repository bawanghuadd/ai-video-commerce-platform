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

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()