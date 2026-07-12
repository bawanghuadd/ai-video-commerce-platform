from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    UserResponse,
)
from app.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)


router = APIRouter(
    prefix="/api/auth",
    tags=["用户认证"],
)


def build_login_response(
    user: User,
) -> LoginResponse:
    """生成用户信息和访问令牌。"""

    user_response = UserResponse.model_validate(
        user
    )

    access_token = create_access_token(
        subject=user.username,
        extra_data={
            "user_id": user.id,
            "role": user.role,
        },
    )

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_response,
    )


@router.post("/login")
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db),
) -> dict:
    """账号密码登录。"""

    user = db.scalar(
        select(User).where(
            User.username
            == login_data.username
        )
    )

    if (
        user is None
        or not verify_password(
            login_data.password,
            user.password_hash,
        )
    ):
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail="用户名或密码错误",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    if not user.is_active:
        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
            detail="当前账号已被停用",
        )

    login_result = build_login_response(
        user
    )

    return {
        "code": 200,
        "message": "登录成功",
        "data": login_result.model_dump(),
    }


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
)
def register(
    register_data: RegisterRequest,
    db: Session = Depends(get_db),
) -> dict:
    """
    注册普通用户。

    注册成功后直接返回访问令牌，
    前端可以自动进入管理系统。
    """

    existing_user = db.scalar(
        select(User).where(
            User.username
            == register_data.username
        )
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail="该账号已经存在",
        )

    user = User(
        username=register_data.username,
        display_name=(
            register_data.display_name
        ),
        password_hash=hash_password(
            register_data.password
        ),
        role="user",
        is_active=True,
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except IntegrityError as error:
        db.rollback()

        raise HTTPException(
            status_code=(
                status.HTTP_409_CONFLICT
            ),
            detail="该账号已经存在",
        ) from error

    login_result = build_login_response(
        user
    )

    return {
        "code": 201,
        "message": "注册成功",
        "data": login_result.model_dump(),
    }


@router.get("/me")
def get_my_profile(
    current_user: User = Depends(
        get_current_user
    ),
) -> dict:
    """获取当前登录用户。"""

    return {
        "code": 200,
        "message": "获取用户信息成功",
        "data": UserResponse.model_validate(
            current_user
        ).model_dump(),
    }