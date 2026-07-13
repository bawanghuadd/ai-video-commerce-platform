from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import AuthenticationError
from app.core.security import decode_access_token
from app.database import get_db
from app.models.user import User


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise AuthenticationError("请先登录")
    payload = decode_access_token(credentials.credentials)
    username = payload.get("sub")
    if not isinstance(username, str):
        raise AuthenticationError("登录凭证无效")
    user = db.scalar(select(User).where(User.username == username))
    if user is None or not user.is_active:
        raise AuthenticationError("用户不存在或已被停用")
    return user
