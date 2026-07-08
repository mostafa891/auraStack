# apps/users/services.py
from django.http import HttpRequest

from apps.users.adapters.allauth import AllauthAdapter
from common.logger import security_logger
from common.results import ServiceResult


class AuthService:
    """طبقة خدمات الهوية لإدارة المعاملات الأمنية وتتبع المؤشرات الحركية."""

    @staticmethod
    def _get_metadata(request: HttpRequest) -> dict:
        """استخراج بيانات العميل للـ Audit Trail بأمان."""
        return {
            "ip": request.META.get("REMOTE_ADDR"),
            "ua": request.META.get("HTTP_USER_AGENT", "Unknown"),
        }

    @classmethod
    def login_user(cls, request: HttpRequest, cleaned_email: str, password: str) -> ServiceResult:
        meta = cls._get_metadata(request)
        result = AllauthAdapter.authenticate_user(
            request=request, email=cleaned_email, password=password
        )

        if not result.success:
            security_logger.warning(
                "Security Event: Failed login for [%s] - Reason: %s - IP: %s - UA: %s",
                cleaned_email,
                result.code,
                meta["ip"],
                meta["ua"],
            )
            return result

        security_logger.info(
            "Security Event: User [%s] logged in successfully - IP: %s", cleaned_email, meta["ip"]
        )
        return result

    @classmethod
    def register_user(
        cls, request: HttpRequest, cleaned_email: str, password: str
    ) -> ServiceResult:
        meta = cls._get_metadata(request)
        result = AllauthAdapter.register_user(
            request=request, email=cleaned_email, password=password
        )

        if not result.success:
            security_logger.warning(
                "Security Event: Registration failed for [%s] - Reason: %s - IP: %s",
                cleaned_email,
                result.code,
                meta["ip"],
            )
            return result

        user_id = getattr(result.data, "id", "Unknown")
        security_logger.info(
            "Security Event: New account created [%s] - UserID: %s - IP: %s",
            cleaned_email,
            user_id,
            meta["ip"],
        )
        return result
