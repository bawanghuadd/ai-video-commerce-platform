import os
from collections.abc import Generator
from pathlib import Path

# Force a non-production, non-writing configuration before importing app modules.
# TEST_DATABASE_URL remains the only opt-in database used by integration tests.
os.environ.update(
    {
        "APP_ENV": "test",
        "DB_HOST": "127.0.0.1",
        "DB_PORT": "3306",
        "DB_USER": "test_only",
        "DB_PASSWORD": "test_only",
        "DB_NAME": "ai_video_commerce_ci",
        "SECRET_KEY": "test-only-secret-not-used-outside-tests",
        "AUTO_CREATE_SCHEMA": "false",
        "SEED_ADMIN": "false",
        "SEED_SYSTEM_SETTINGS": "false",
    }
)

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker

from app.core.security import create_access_token, hash_password
from app.database import Base, get_db
from app.main import fastapi_app
from app.models.user import User

# Import every model before creating the isolated schema.
from app.models import content_analysis, knowledge, product, script, system_setting, video_task  # noqa: F401,E501


SAFE_DATABASE_MARKERS = ("test", "testing", "ci")


def validate_test_database_url(database_url: str) -> str:
    """Reject any explicit test URL whose database name is not clearly isolated."""

    parsed = make_url(database_url)
    database_name = (parsed.database or "").lower()
    if not any(marker in database_name for marker in SAFE_DATABASE_MARKERS):
        raise RuntimeError(
            "TEST_DATABASE_URL database name must include test, testing, or ci"
        )
    return database_url


def resolve_test_database_url(tmp_path_factory: pytest.TempPathFactory) -> str:
    explicit_url = os.getenv("TEST_DATABASE_URL")
    if explicit_url:
        return validate_test_database_url(explicit_url)
    database_path = tmp_path_factory.mktemp("database") / "phase2_test.sqlite3"
    return f"sqlite+pysqlite:///{database_path.as_posix()}"


@pytest.fixture(scope="session")
def test_database_url(tmp_path_factory: pytest.TempPathFactory) -> str:
    return resolve_test_database_url(tmp_path_factory)


@pytest.fixture(scope="session")
def test_engine(test_database_url: str):
    connect_args = {"check_same_thread": False} if test_database_url.startswith("sqlite") else {}
    engine = create_engine(test_database_url, connect_args=connect_args)
    if test_database_url.startswith("sqlite"):
        @event.listens_for(engine, "connect")
        def enable_sqlite_foreign_keys(dbapi_connection, _):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
    yield engine
    engine.dispose()


@pytest.fixture()
def db_session(test_engine) -> Generator[Session, None, None]:
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    testing_session = sessionmaker(bind=test_engine, expire_on_commit=False)
    with testing_session() as session:
        yield session
        session.rollback()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db():
        yield db_session

    fastapi_app.dependency_overrides[get_db] = override_get_db
    with TestClient(fastapi_app, raise_server_exceptions=False) as test_client:
        yield test_client
    fastapi_app.dependency_overrides.clear()


@pytest.fixture()
def users(db_session: Session) -> dict[str, User]:
    result = {}
    for role in ("admin", "editor", "viewer"):
        user = User(
            username=f"{role}_user",
            display_name=f"{role.title()} User",
            password_hash=hash_password("isolated-strong-password"),
            role=role,
            is_active=True,
        )
        db_session.add(user)
        result[role] = user
    db_session.commit()
    return result


@pytest.fixture()
def auth_headers(users: dict[str, User]) -> dict[str, dict[str, str]]:
    return {
        role: {"Authorization": f"Bearer {create_access_token(user.username, {'role': role})}"}
        for role, user in users.items()
    }
