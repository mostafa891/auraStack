from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class AuthErrorCode(StrEnum):
    """رموز الأخطاء الصارمة الموحدة لمنظومة الهوية."""

    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    ACCOUNT_LOCKED = "ACCOUNT_LOCKED"
    ACCOUNT_INACTIVE = "ACCOUNT_INACTIVE"
    EMAIL_ALREADY_EXISTS = "EMAIL_ALREADY_EXISTS"


@dataclass(slots=True)
class ServiceResult:
    """الكائن القياسي الموحد لنقل البيانات والمؤشرات عبر طبقات المنصة."""

    success: bool
    data: Any = None
    errors: dict[str, list[dict[str, Any]]] = None
    code: AuthErrorCode | None = None
    message: str | None = None
