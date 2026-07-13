import pytest
from pydantic import ValidationError

from app.config import Settings


BASE_SETTINGS = {
    "db_user": "test_user",
    "db_password": "test_password",
    "db_name": "test_database",
    "secret_key": "test-secret-that-is-long-enough",
}


def create_settings(**overrides):
    return Settings(
        **BASE_SETTINGS,
        **overrides,
        _env_file=None,
    )


def test_database_bootstrap_is_disabled_by_default():
    settings = create_settings()

    assert settings.auto_create_schema is False
    assert settings.seed_admin is False
    assert settings.seed_system_settings is False


@pytest.mark.parametrize(
    "flag",
    [
        "auto_create_schema",
        "seed_admin",
        "seed_system_settings",
    ],
)
def test_production_rejects_automatic_database_writes(flag):
    with pytest.raises(ValidationError):
        create_settings(
            app_env="production",
            **{flag: True},
        )


def test_admin_seed_requires_explicit_strong_credentials():
    with pytest.raises(ValidationError):
        create_settings(seed_admin=True)

    with pytest.raises(ValidationError):
        create_settings(
            seed_admin=True,
            admin_bootstrap_username="local_admin",
            admin_bootstrap_password="short",
        )

    settings = create_settings(
        seed_admin=True,
        admin_bootstrap_username="local_admin",
        admin_bootstrap_password="local-only-strong-password",
    )

    assert settings.seed_admin is True
