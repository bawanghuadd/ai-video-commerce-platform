from sqlalchemy.orm import Session

from app.constants.roles import Role, normalize_role
from app.core.exceptions import AuthenticationError, ConflictError, NotFoundError, PermissionDeniedError
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.auth import LoginRequest, LoginResponse, RegisterRequest, UserResponse
from app.services.base import Service, transactional


class AuthService(Service):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.repository = UserRepository(session)

    @staticmethod
    def user_response(user: User) -> UserResponse:
        response = UserResponse.model_validate(user)
        effective_role = normalize_role(user.role)
        if effective_role is not None and response.role != effective_role.value:
            response = response.model_copy(update={"role": effective_role.value})
        return response

    def build_login_response(self, user: User) -> LoginResponse:
        user_response = self.user_response(user)
        token = create_access_token(
            subject=user.username,
            extra_data={"user_id": user.id, "role": user_response.role},
        )
        return LoginResponse(access_token=token, token_type="bearer", user=user_response)

    def login(self, login_data: LoginRequest) -> LoginResponse:
        user = self.repository.get_by_username(login_data.username)
        if user is None or not verify_password(login_data.password, user.password_hash):
            raise AuthenticationError("用户名或密码错误")
        if not user.is_active:
            raise PermissionDeniedError("当前账号已被停用")
        return self.build_login_response(user)

    @transactional("该账号已经存在")
    def register(self, register_data: RegisterRequest) -> LoginResponse:
        if self.repository.get_by_username(register_data.username) is not None:
            raise ConflictError("该账号已经存在")
        user = User(
            username=register_data.username,
            display_name=register_data.display_name,
            password_hash=hash_password(register_data.password),
            role=Role.VIEWER.value,
            is_active=True,
        )
        self.repository.add(user)
        self.repository.flush()
        return self.build_login_response(user)

    @transactional("管理员账号已经存在")
    def create_admin(self, username: str, display_name: str, password: str) -> User:
        if len(password) < 12:
            raise ValueError("管理员密码不能少于12个字符")
        if self.repository.get_by_username(username) is not None:
            raise ConflictError("管理员账号已经存在")
        user = User(
            username=username,
            display_name=display_name,
            password_hash=hash_password(password),
            role=Role.ADMIN.value,
            is_active=True,
        )
        self.repository.add(user)
        self.repository.flush()
        return user

    @transactional("管理员晋升冲突")
    def promote_admin(self, username: str) -> User:
        user = self.repository.get_by_username(username)
        if user is None:
            raise NotFoundError("用户不存在")
        user.role = Role.ADMIN.value
        user.is_active = True
        self.repository.flush()
        return user
