import pytest

from app.schemas.script import ScriptCreate
from app.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hash_and_verify():
    password = "strong-local-password"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong-password", hashed) is False


def test_jwt_create_and_decode():
    token = create_access_token("test_user", {"role": "user"})
    payload = decode_access_token(token)

    assert payload["sub"] == "test_user"
    assert payload["role"] == "user"
    assert "exp" in payload


def test_script_schema_rejects_an_unknown_status():
    with pytest.raises(ValueError):
        ScriptCreate(
            product_id=1,
            title="test",
            status="unknown",
        )
