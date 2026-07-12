from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.user import User


ALGORITHM = "HS256"

password_hash = PasswordHash.recommended()
bearer_scheme = HTTPBearer()


def hash_password(plain_password: str) -> str:
    """将明文密码转换成安全哈希。"""

    return password_hash.hash(plain_password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """验证密码是否正确。"""

    return password_hash.verify(
        plain_password,
        hashed_password,
    )


def create_access_token(
    subject: str,
    extra_data: dict[str, Any] | None = None,
) -> str:
    """创建 JWT 登录令牌。"""

    expire_time = datetime.now(timezone.utc) + timedelta(
        hours=settings.access_token_expire_hours
    )

    payload: dict[str, Any] = {
        "sub": subject,
        "exp": expire_time,
    }

    if extra_data:
        payload.update(extra_data)

    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=ALGORITHM,
    )


def decode_access_token(token: str) -> dict[str, Any]:
    """解析 JWT 登录令牌。"""

    try:
        return jwt.decode(
            token,
            settings.secret_key,
            algorithms=[ALGORITHM],
        )
    except InvalidTokenError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="登录状态无效或已经过期",
            headers={"WWW-Authenticate": "Bearer"},
        ) from error


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        bearer_scheme
    ),
    db: Session = Depends(get_db),
) -> User:
    """根据 JWT 从数据库查询当前用户。"""

    payload = decode_access_token(
        credentials.credentials
    )

    username = payload.get("sub")

    if not isinstance(username, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="登录凭证无效",
        )

    statement = select(User).where(
        User.username == username
    )

    user = db.scalar(statement)

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被停用",
        )

    return user