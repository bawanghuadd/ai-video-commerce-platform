from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

from app.core.config import settings
from app.core.exceptions import AuthenticationError


ALGORITHM = "HS256"
password_hash = PasswordHash.recommended()


def hash_password(plain_password: str) -> str:
    return password_hash.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(subject: str, extra_data: dict[str, Any] | None = None) -> str:
    expire_time = datetime.now(timezone.utc) + timedelta(hours=settings.access_token_expire_hours)
    payload: dict[str, Any] = {"sub": subject, "exp": expire_time}
    if extra_data:
        payload.update(extra_data)
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    except InvalidTokenError as error:
        raise AuthenticationError("登录状态无效或已经过期") from error
