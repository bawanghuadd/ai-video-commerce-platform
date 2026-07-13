from sqlalchemy import select

from app.models.system_setting import SystemSetting


def test_get_settings_returns_defaults_without_implicit_write(client, auth_headers, db_session):
    response = client.get("/api/system-settings", headers=auth_headers["viewer"])
    assert response.status_code == 200
    assert response.json()["data"]["id"] == 1
    assert db_session.scalar(select(SystemSetting)) is None


def test_explicit_update_creates_and_updates_singleton(client, auth_headers, db_session):
    response = client.put(
        "/api/system-settings",
        headers=auth_headers["admin"],
        json={"platform_name": "隔离测试平台", "temperature": 1.1},
    )
    assert response.status_code == 200
    assert response.json()["data"]["platform_name"] == "隔离测试平台"
    rows = list(db_session.scalars(select(SystemSetting)).all())
    assert len(rows) == 1
    assert rows[0].id == 1
