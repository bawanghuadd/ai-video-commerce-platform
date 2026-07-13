from collections.abc import Callable

from fastapi import Depends, Request

from app.constants.roles import Role, normalize_role
from app.core.exceptions import PermissionDeniedError
from app.dependencies.auth import get_current_user


def require_roles(*allowed_roles: Role) -> Callable:
    allowed = set(allowed_roles)

    def dependency(current_user=Depends(get_current_user)):
        if normalize_role(current_user.role) not in allowed:
            raise PermissionDeniedError("当前账号无权限执行此操作")
        return current_user

    return dependency


def require_business_access(
    request: Request,
    current_user=Depends(get_current_user),
):
    role = normalize_role(current_user.role)
    if role is None:
        raise PermissionDeniedError("当前账号无权限执行此操作")
    if request.method not in {"GET", "HEAD", "OPTIONS"} and role not in {
        Role.ADMIN,
        Role.EDITOR,
    }:
        raise PermissionDeniedError("当前账号无权限执行此操作")
    return current_user


def require_settings_access(
    request: Request,
    current_user=Depends(get_current_user),
):
    role = normalize_role(current_user.role)
    if role is None:
        raise PermissionDeniedError("当前账号无权限执行此操作")
    if request.method not in {"GET", "HEAD", "OPTIONS"} and role is not Role.ADMIN:
        raise PermissionDeniedError("当前账号无权限执行此操作")
    return current_user


require_business_write = require_roles(Role.ADMIN, Role.EDITOR)
require_admin = require_roles(Role.ADMIN)