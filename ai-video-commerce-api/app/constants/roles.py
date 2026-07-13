from enum import StrEnum


class Role(StrEnum):
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"


LEGACY_ROLE_MAP = {"user": Role.EDITOR}


def normalize_role(role: str) -> Role | None:
    if role in LEGACY_ROLE_MAP:
        return LEGACY_ROLE_MAP[role]
    try:
        return Role(role)
    except ValueError:
        return None
