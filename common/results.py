from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class AuthErrorCode(StrEnum):
    """Standardized authentication error code definitions."""

    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    ACCOUNT_LOCKED = "ACCOUNT_LOCKED"
    ACCOUNT_INACTIVE = "ACCOUNT_INACTIVE"
    EMAIL_ALREADY_EXISTS = "EMAIL_ALREADY_EXISTS"


@dataclass(slots=True)
class ServiceResult:
    """Standard container for service layer responses and operation state."""

    success: bool
    data: Any = None
    errors: dict[str, list[dict[str, Any]]] = None
    code: AuthErrorCode | None = None
    message: str | None = None
