from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text


def test_role_migration_upgrade_downgrade_upgrade(tmp_path, monkeypatch):
    database_path = tmp_path / "alembic_ci.sqlite3"
    database_url = f"sqlite+pysqlite:///{database_path.as_posix()}"
    monkeypatch.setenv("ALEMBIC_DATABASE_URL", database_url)
    config = Config("alembic.ini")

    command.upgrade(config, "20260713_0001")
    engine = create_engine(database_url)
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO users (username, display_name, password_hash) "
                "VALUES ('legacy', 'Legacy', 'hash')"
            )
        )

    command.upgrade(config, "head")
    with engine.connect() as connection:
        assert connection.scalar(
            text("SELECT role FROM users WHERE username = 'legacy'")
        ) == "editor"

    command.downgrade(config, "-1")
    with engine.connect() as connection:
        assert connection.scalar(
            text("SELECT role FROM users WHERE username = 'legacy'")
        ) == "user"

    command.upgrade(config, "head")
    with engine.connect() as connection:
        assert connection.scalar(
            text("SELECT role FROM users WHERE username = 'legacy'")
        ) == "editor"
    engine.dispose()
