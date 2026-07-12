# apps/users/adapters/allauth.py
from allauth.account.adapter import DefaultAccountAdapter, get_adapter
from allauth.account.forms import LoginForm
from allauth.account.utils import complete_signup
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import HttpRequest

from common.results import AuthErrorCode, ServiceResult


class CustomAccountAdapter(DefaultAccountAdapter):
    def is_ajax(self, request: HttpRequest) -> bool:
        if request.headers.get("x-inertia") or request.META.get("HTTP_X_INERTIA"):
            return False
        return super().is_ajax(request)


class AllauthAdapter:
    """المحول المباشر لإدارة وتطويع الـ APIs المستقرة لـ django-allauth."""

    @staticmethod
    def authenticate_user(
        request: HttpRequest, email: str, password: str, remember: bool = False
    ) -> ServiceResult:
        form = LoginForm(
            request=request, data={"login": email, "password": password, "remember": remember}
        )

        if not form.is_valid():
            errors = form.errors.get_json_data()
            error_code = AuthErrorCode.INVALID_CREDENTIALS
            if form.errors.as_data().get("__all__"):
                for error in form.errors.as_data()["__all__"]:
                    if error.code == "account_inactive":
                        error_code = AuthErrorCode.ACCOUNT_INACTIVE
            return ServiceResult(success=False, errors=errors, code=error_code)

        response = form.login(request)
        return ServiceResult(success=True, data=response)

    @staticmethod
    def register_user(request: HttpRequest, email: str, password: str) -> ServiceResult:
        """إنشاء مستخدم جديد بالكامل عبر الـ Adapter API الرسمية والمستقرة لـ allauth."""
        adapter = get_adapter(request)
        user = adapter.new_user(request)
        user.email = email

        try:
            # تشغيل سياسات فحص قوة كلمة المرور الرسمية لـ دجانغو وallauth
            adapter.clean_password(password, user)
            user.set_password(password)

            # الحفظ الصارم في قاعدة البيانات - سيطلق الـ IntegrityError فوراً لو كان البريد مكرراً
            user.save()

            # تهيئة البريد الإلكتروني في جداول Allauth لضمان إنشاء سجل EmailAddress
            from allauth.account.utils import setup_user_email

            setup_user_email(request, user, [])

            # إكمال المعاملة الخلفية لـ allauth (إطلاق الـ Signals، وتجهيز بريد التفعيل)
            complete_signup(
                request=request,
                user=user,
                email_verification="none",  # محكوم بالـ Settings الافتراضية للـ local
                success_url="/",
            )
            return ServiceResult(success=True, data=user)

        except ValidationError as e:
            # بما أن الخطأ يتم إطلاقه من clean_password، فهو دائماً يتعلق بحقل كلمة المرور
            errors = e.message_dict if hasattr(e, "error_dict") else {"password": e.messages}
            return ServiceResult(
                success=False, errors=errors, code=AuthErrorCode.INVALID_CREDENTIALS
            )
        except IntegrityError:
            # صيد ثغرة الـ Race Condition من المنبع (قاعدة البيانات)
            return ServiceResult(success=False, code=AuthErrorCode.EMAIL_ALREADY_EXISTS)
