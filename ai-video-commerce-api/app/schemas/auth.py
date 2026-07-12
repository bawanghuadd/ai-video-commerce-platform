import re

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class LoginRequest(BaseModel):
    """用户登录请求。"""

    username: str = Field(
        min_length=1,
        max_length=50,
        description="登录账号",
        examples=["admin"],
    )

    password: str = Field(
        min_length=6,
        max_length=100,
        description="登录密码",
        examples=["123456"],
    )

    @field_validator("username")
    @classmethod
    def normalize_username(
        cls,
        value: str,
    ) -> str:
        """去除账号前后的空格。"""

        username = value.strip()

        if not username:
            raise ValueError("账号不能为空")

        return username


class RegisterRequest(BaseModel):
    """用户注册请求。"""

    username: str = Field(
        min_length=3,
        max_length=50,
        description="注册账号",
        examples=["testuser"],
    )

    display_name: str = Field(
        min_length=1,
        max_length=50,
        description="用户昵称",
        examples=["测试用户"],
    )

    password: str = Field(
        min_length=6,
        max_length=100,
        description="注册密码",
        examples=["123456"],
    )

    @field_validator("username")
    @classmethod
    def validate_username(
        cls,
        value: str,
    ) -> str:
        """
        校验注册账号。

        账号只允许使用：
        - 英文字母
        - 数字
        - 下划线
        """

        username = value.strip()

        if not username:
            raise ValueError("账号不能为空")

        if not re.fullmatch(
            r"[A-Za-z0-9_]+",
            username,
        ):
            raise ValueError(
                "账号只能包含英文字母、数字和下划线"
            )

        return username

    @field_validator("display_name")
    @classmethod
    def normalize_display_name(
        cls,
        value: str,
    ) -> str:
        """去除昵称前后的空格。"""

        display_name = value.strip()

        if not display_name:
            raise ValueError("昵称不能为空")

        return display_name

    @field_validator("password")
    @classmethod
    def validate_password(
        cls,
        value: str,
    ) -> str:
        """校验密码不能全部为空格。"""

        if not value.strip():
            raise ValueError("密码不能为空")

        return value


class UserResponse(BaseModel):
    """返回给前端的用户信息。"""

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    username: str
    display_name: str
    role: str
    is_active: bool


class LoginResponse(BaseModel):
    """
    登录或注册成功后的认证数据。

    注册成功后同样返回该结构，
    让前端能够直接保存 JWT 并自动登录。
    """

    access_token: str
    token_type: str = "bearer"
    user: UserResponse