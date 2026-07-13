PRODUCT = {
    "product_name": "权限商品",
    "category": "测试",
    "price": 1,
    "stock": 1,
}


def test_viewer_can_read_but_cannot_write(client, auth_headers):
    read = client.get("/api/products", headers=auth_headers["viewer"])
    assert read.status_code == 200
    write = client.post("/api/products", headers=auth_headers["viewer"], json=PRODUCT)
    assert write.status_code == 403
    assert write.json() == {"detail": "当前账号无权限执行此操作"}


def test_editor_can_write_business_but_not_settings(client, auth_headers):
    business = client.post("/api/products", headers=auth_headers["editor"], json=PRODUCT)
    assert business.status_code == 201
    settings = client.put(
        "/api/system-settings",
        headers=auth_headers["editor"],
        json={"platform_name": "forbidden"},
    )
    assert settings.status_code == 403


def test_admin_can_write_settings(client, auth_headers):
    response = client.put(
        "/api/system-settings",
        headers=auth_headers["admin"],
        json={"platform_name": "admin allowed"},
    )
    assert response.status_code == 200


def test_inactive_user_token_is_unauthenticated(client, db_session):
    from app.core.security import create_access_token, hash_password
    from app.models.user import User

    user = User(
        username="inactive_token",
        display_name="Inactive",
        password_hash=hash_password("strong-password"),
        role="admin",
        is_active=False,
    )
    db_session.add(user)
    db_session.commit()
    token = create_access_token(user.username, {"role": "admin"})
    response = client.get(
        "/api/products",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401
