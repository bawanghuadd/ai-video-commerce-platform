from app.models.product import Product


PRODUCT_DATA = {
    "product_name": "隔离测试商品",
    "category": "测试分类",
    "price": 99.5,
    "stock": 10,
    "selling_points": "测试卖点",
    "target_audience": "测试用户",
}


def test_products_require_authentication(client):
    response = client.get("/api/products")
    assert response.status_code == 401
    assert response.json() == {"detail": "请先登录"}


def test_product_crud_preserves_envelope_and_list_array(client, auth_headers):
    created = client.post("/api/products", json=PRODUCT_DATA, headers=auth_headers["admin"])
    assert created.status_code == 201
    assert created.json()["code"] == 201
    product_id = created.json()["data"]["id"]

    listed = client.get("/api/products", headers=auth_headers["admin"])
    assert listed.status_code == 200
    assert isinstance(listed.json()["data"], list)
    assert listed.json()["data"][0]["id"] == product_id

    updated = client.put(
        f"/api/products/{product_id}",
        json={"stock": 8},
        headers=auth_headers["admin"],
    )
    assert updated.status_code == 200
    assert updated.json()["data"]["stock"] == 8

    deleted = client.delete(f"/api/products/{product_id}", headers=auth_headers["admin"])
    assert deleted.status_code == 200
    assert deleted.json()["data"] is None


def test_product_errors_are_stable(client, auth_headers):
    missing = client.get("/api/products/999", headers=auth_headers["admin"])
    assert missing.status_code == 404
    assert missing.json() == {"detail": "商品不存在"}

    invalid = client.post(
        "/api/products",
        json={**PRODUCT_DATA, "price": 0},
        headers=auth_headers["admin"],
    )
    assert invalid.status_code == 422


def test_product_write_rolls_back_when_flush_fails(db_session, monkeypatch):
    from app.services.product import ProductService

    service = ProductService(db_session)
    rollback_called = False

    def fail_flush():
        raise RuntimeError("simulated failure")

    def record_rollback():
        nonlocal rollback_called
        rollback_called = True

    monkeypatch.setattr(service.repository, "flush", fail_flush)
    monkeypatch.setattr(db_session, "rollback", record_rollback)

    try:
        service.create_product(ProductCreateForTest())
    except RuntimeError:
        pass

    assert rollback_called is True


def ProductCreateForTest():
    from app.schemas.product import ProductCreate

    return ProductCreate(**PRODUCT_DATA)
