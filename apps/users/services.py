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
    def login_user(
        cls, request: HttpRequest, cleaned_email: str, password: str, remember: bool = False
    ) -> ServiceResult:
        meta = cls._get_metadata(request)
        result = AllauthAdapter.authenticate_user(
            request=request, email=cleaned_email, password=password, remember=remember
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

        # إرسال البريد الترحيبي
        from django.conf import settings
        from django.core.mail import send_mail
        from django.template.loader import render_to_string

        try:
            site_url = getattr(settings, "SITE_URL", "http://localhost:8000")
            html_message = render_to_string("emails/welcome.html", {"site_url": site_url})
            send_mail(
                subject="Welcome to AuraFlow!",
                message="Welcome to AuraFlow! Your account is now active.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[cleaned_email],
                html_message=html_message,
            )
        except Exception as e:
            security_logger.error("Failed to send welcome email: %s", str(e))

        user_id = getattr(result.data, "id", "Unknown")
        security_logger.info(
            "Security Event: New account created [%s] - UserID: %s - IP: %s",
            cleaned_email,
            user_id,
            meta["ip"],
        )
        return result


class UserService:
    """طبقة خدمات المستخدم لإدارة وتحديث البيانات الشخصية والتفضيلات."""

    @staticmethod
    def update_profile_preferences(
        user, language: str, theme: str, timezone: str, avatar_url: str = None
    ) -> ServiceResult:
        try:
            user.language = language
            user.theme = theme
            user.timezone = timezone
            if avatar_url is not None:
                user.avatar_url = avatar_url
            user.save()
            return ServiceResult(success=True, data=user, message="Profile updated successfully")
        except Exception as e:
            return ServiceResult(success=False, message=f"Failed to update profile: {str(e)}")
