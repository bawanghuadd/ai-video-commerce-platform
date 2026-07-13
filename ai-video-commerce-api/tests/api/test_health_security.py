import logging

from sqlalchemy.exc import OperationalError

from app.api.products import get_product_service
from app.database import get_db
from app.main import fastapi_app


def test_readiness_returns_503_without_database_details(client):
    class BrokenSession:
        def execute(self, *_args, **_kwargs):
            raise OperationalError("SELECT 1", {}, RuntimeError("private-db-host"))

    def broken_db():
        yield BrokenSession()

    fastapi_app.dependency_overrides[get_db] = broken_db
    response = client.get("/health/ready")
    assert response.status_code == 503
    assert response.json() == {"detail": "数据库暂不可用"}
    assert "private-db-host" not in response.text


def test_unexpected_error_returns_generic_500(client, auth_headers):
    def fail_service():
        raise RuntimeError("secret-token-value")

    fastapi_app.dependency_overrides[get_product_service] = fail_service
    response = client.get("/api/products", headers=auth_headers["admin"])
    assert response.status_code == 500
    assert response.json() == {"detail": "服务器内部错误，请稍后重试"}
    assert "secret-token-value" not in response.text


def test_request_log_does_not_include_authorization(client, caplog):
    caplog.set_level(logging.INFO, logger="app.request")
    secret = "Bearer should-never-be-logged"
    response = client.get("/health/live", headers={"Authorization": secret})
    assert response.status_code == 200
    assert "method=GET" in caplog.text
    assert "path=/health/live" in caplog.text
    assert secret not in caplog.text
