"""Compatibility exports for the Phase 1 security path."""

from app.core.security import (
    ALGORITHM,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.dependencies.auth import bearer_scheme, get_current_user

__all__ = [
    "ALGORITHM",
    "bearer_scheme",
    "create_access_token",
    "decode_access_token",
    "get_current_user",
    "hash_password",
    "verify_password",
]