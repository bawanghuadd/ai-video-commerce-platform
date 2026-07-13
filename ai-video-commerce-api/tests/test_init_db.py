from app import init_db


def test_default_initialization_does_not_touch_database(monkeypatch):
    monkeypatch.setattr(init_db.settings, "auto_create_schema", False)
    monkeypatch.setattr(init_db.settings, "seed_admin", False)
    monkeypatch.setattr(init_db.settings, "seed_system_settings", False)

    create_all_called = False

    def fail_create_all(*_args, **_kwargs):
        nonlocal create_all_called
        create_all_called = True

    monkeypatch.setattr(
        init_db.Base.metadata,
        "create_all",
        fail_create_all,
    )

    class FailSession:
        def __call__(self):
            raise AssertionError("default startup must not open a database session")

    monkeypatch.setattr(init_db, "SessionLocal", FailSession())

    init_db.init_db()

    assert create_all_called is False
