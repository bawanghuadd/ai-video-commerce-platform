from app.core.security import create_access_token, hash_password
from app.models.user import User


def test_register_login_and_me_never_return_password(client):
    registered = client.post(
        "/api/auth/register",
        json={"username": "new_viewer", "display_name": "New Viewer", "password": "strong-password"},
    )
    assert registered.status_code == 201
    body = registered.json()
    assert body["data"]["user"]["role"] == "viewer"
    assert "password" not in str(body).lower()

    token = body["data"]["access_token"]
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["data"]["username"] == "new_viewer"
    assert "password_hash" not in me.json()["data"]

    login = client.post(
        "/api/auth/login",
        json={"username": "new_viewer", "password": "strong-password"},
    )
    assert login.status_code == 200


def test_duplicate_and_disabled_user_semantics(client, db_session):
    user = User(
        username="disabled",
        display_name="Disabled",
        password_hash=hash_password("strong-password"),
        role="viewer",
        is_active=False,
    )
    db_session.add(user)
    db_session.commit()
    disabled = client.post(
        "/api/auth/login",
        json={"username": "disabled", "password": "strong-password"},
    )
    assert disabled.status_code == 403

    payload = {"username": "duplicate", "display_name": "Duplicate", "password": "strong-password"}
    assert client.post("/api/auth/register", json=payload).status_code == 201
    assert client.post("/api/auth/register", json=payload).status_code == 409


def test_token_role_claim_does_not_override_database_role(client, users):
    forged = create_access_token(users["viewer"].username, {"role": "admin"})
    response = client.post(
        "/api/products",
        headers={"Authorization": f"Bearer {forged}"},
        json={"product_name": "forged", "category": "test", "price": 1, "stock": 1},
    )
    assert response.status_code == 403
