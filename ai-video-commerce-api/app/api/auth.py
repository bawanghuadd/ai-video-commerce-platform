from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.schemas.auth import LoginRequest, LoginResponse, RegisterRequest, UserResponse
from app.schemas.common import ApiResponse
from app.services.auth import AuthService


router = APIRouter(prefix="/api/auth", tags=["用户认证"])


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)


@router.post("/login", response_model=ApiResponse[LoginResponse])
def login(
    login_data: LoginRequest,
    service: AuthService = Depends(get_auth_service),
) -> dict:
    return {"code": 200, "message": "登录成功", "data": service.login(login_data)}


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiResponse[LoginResponse],
)
def register(
    register_data: RegisterRequest,
    service: AuthService = Depends(get_auth_service),
) -> dict:
    return {"code": 201, "message": "注册成功", "data": service.register(register_data)}


@router.get("/me", response_model=ApiResponse[UserResponse])
def get_my_profile(
    current_user=Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
) -> dict:
    return {
        "code": 200,
        "message": "获取用户信息成功",
        "data": service.user_response(current_user),
    }