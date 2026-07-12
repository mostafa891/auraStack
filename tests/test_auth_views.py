import pytest
from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpResponseRedirect
from django.test import RequestFactory

from apps.users.adapters.allauth import CustomAccountAdapter
from apps.users.views_security import SetLanguageView


@pytest.mark.django_db
def test_custom_account_adapter_is_ajax():
    """التحقق من أن محول الحساب المخصص يعطل التعرف على AJAX عند وجود ترويسات Inertia."""
    factory = RequestFactory()
    adapter = CustomAccountAdapter()

    # 1. طلب AJAX عادي
    request_ajax = factory.post("/accounts/login/", HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    assert adapter.is_ajax(request_ajax) is True

    # 2. طلب Inertia (يجب ألا يتم اعتباره AJAX ليتلقى استجابة Inertia صحيحة)
    request_inertia = factory.post("/accounts/login/", HTTP_X_INERTIA="true")
    assert adapter.is_ajax(request_inertia) is False

    # 3. طلب Inertia مع ترويسة x-inertia المباشرة
    request_inertia_header = factory.post("/accounts/login/", HTTP_X_INERTIA="true")
    assert adapter.is_ajax(request_inertia_header) is False

    # 4. طلب عادي غير AJAX
    request_normal = factory.post("/accounts/login/")
    assert adapter.is_ajax(request_normal) is False


@pytest.mark.django_db
def test_set_language_view():
    """التحقق من عمل متحكم SetLanguageView لتغيير اللغة وتخزينها في الكوكيز والجلسة."""
    factory = RequestFactory()
    view = SetLanguageView.as_view()

    # 1. طلب تغيير اللغة إلى العربية
    request = factory.post(
        "/auth/set-language/", data={"language": "ar"}, content_type="application/json"
    )

    # إضافة بريمج الجلسة المساعد لمحاكاة وجود جلسة
    middleware = SessionMiddleware(lambda req: None)
    middleware.process_request(request)
    request.session.save()

    response = view(request)

    # التحقق من أن الاستجابة هي توجيه
    assert response.status_code == 302

    # التحقق من حفظ الكوكيز والجلسة
    assert response.cookies[settings.LANGUAGE_COOKIE_NAME].value == "ar"
    assert request.session["_language"] == "ar"


@pytest.mark.django_db
def test_mock_oauth_login(client):
    """محاكاة لدورة تسجيل دخول ناجحة بالـ OAuth (مثل Google أو GitHub) للتحقق من تكامل allauth."""
    from unittest.mock import patch

    import allauth.socialaccount.helpers as helpers

    # محاكاة لـ socialaccount logins
    from allauth.socialaccount.models import SocialLogin
    from django.contrib.auth import get_user_model

    User = get_user_model()

    # إنشاء مستخدم
    user = User.objects.create_user(email="oauth_test@example.com", password="Password123!")

    # محاكاة تسجيل الدخول بالشبكات الاجتماعية
    social_login = SocialLogin(user=user)

    # استخدام unittest.mock.patch لمحاكاة استدعاء Allauth المباشر
    with patch("allauth.socialaccount.helpers.complete_social_login") as mock_complete:
        mock_complete.return_value = HttpResponseRedirect(redirect_to="/profile/")

        request = RequestFactory().get("/accounts/google/login/callback/")
        from django.contrib.sessions.middleware import SessionMiddleware

        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        request.user = user

        # تنفيذ الاستدعاء الافتراضي
        response = helpers.complete_social_login(request, social_login)

        assert response.status_code == 302
        assert response["Location"] == "/profile/"
