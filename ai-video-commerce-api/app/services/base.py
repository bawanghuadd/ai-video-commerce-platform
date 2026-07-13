from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError


F = TypeVar("F", bound=Callable[..., Any])


def transactional(conflict_message: str = "数据冲突"):
    """Commit one service operation and always rollback on failure."""

    def decorator(function: F) -> F:
        @wraps(function)
        def wrapper(self, *args, **kwargs):
            try:
                result = function(self, *args, **kwargs)
                self.session.commit()
                return result
            except IntegrityError as error:
                self.session.rollback()
                raise ConflictError(conflict_message) from error
            except Exception:
                self.session.rollback()
                raise

        return wrapper

    return decorator


class Service:
    def __init__(self, session: Session) -> None:
        self.session = session
