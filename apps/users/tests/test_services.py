import pytest
from allauth.core import context

from apps.users.models import CustomUser
from apps.users.services import AuthService
from common.results import AuthErrorCode


@pytest.mark.django_db
def test_login_user_incorrect_credentials(client, test_user):
    """التحقق من فشل المصادقة عند استخدام كلمة مرور خاطئة."""
    request = client.request().wsgi_request
    with context.request_context(request):
        result = AuthService.login_user(
            request=request,
            cleaned_email=test_user.email,
            password="WrongPassword!",
        )
    assert result.success is False
    assert result.code == AuthErrorCode.INVALID_CREDENTIALS


@pytest.mark.django_db
def test_register_user_duplicate_email(client, test_user):
    """التحقق من منع تسجيل حساب ببريد إلكتروني مسجل مسبقاً."""
    request = client.request().wsgi_request
    with context.request_context(request):
        result = AuthService.register_user(
            request=request,
            cleaned_email=test_user.email,
            password="NewPassword123!",
        )
    assert result.success is False
    assert result.code == AuthErrorCode.EMAIL_ALREADY_EXISTS


@pytest.mark.django_db
def test_register_user_successful(client):
    """التحقق من نجاح التسجيل واستدعاء دورة إنشاء حساب allauth."""
    request = client.request().wsgi_request
    email = "new_signup@auraflow.com"
    with context.request_context(request):
        result = AuthService.register_user(
            request=request,
            cleaned_email=email,
            password="ValidPassword123!",
        )
    assert result.success is True
    assert CustomUser.objects.filter(email=email).exists() is True
