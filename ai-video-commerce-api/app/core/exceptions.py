class DomainError(Exception):
    """Base exception for errors safe to map to an API response."""

    status_code = 500

    def __init__(self, message: str = "操作失败") -> None:
        self.message = message
        super().__init__(message)


class AuthenticationError(DomainError):
    status_code = 401


class PermissionDeniedError(DomainError):
    status_code = 403


class NotFoundError(DomainError):
    status_code = 404


class ConflictError(DomainError):
    status_code = 409


class ValidationError(DomainError):
    status_code = 422
