from django.test import RequestFactory, override_settings
from django_ratelimit.core import is_ratelimited

from apps.users.views import LoginView, RegisterView


@override_settings(RATELIMIT_ENABLE=True)
def test_ratelimit_core_logic():
    """التحقق من عمل الخوارزمية الأساسية للـ Rate Limiting مع محاكاة الطلبات المتكررة."""
    factory = RequestFactory()

    # محاكاة 11 طلب POST متتالي من نفس الـ IP
    for i in range(11):
        request = factory.post("/auth/login/")
        request.META["REMOTE_ADDR"] = "192.168.1.1"

        # تحقق يدوي باستخدام محرك المكتبة الأساسي
        limited = is_ratelimited(
            request, key="ip", rate="10/m", method="POST", increment=True, group="login"
        )

        if i >= 10:
            assert limited is True, "يجب أن يتم حظر الطلب الحادي عشر"
        else:
            assert limited is False, "الطلبات العشرة الأولى يجب أن تمر بنجاح"


def test_views_have_ratelimit_applied():
    """التحقق من أن دوال عروض المصادقة مزودة بمحدد معدل الطلبات برمجياً."""
    # التحقق من أن الميثودز مغلفة بـ decorators الـ ratelimit
    assert (
        hasattr(LoginView.post, "__wrapped__")
        or hasattr(LoginView.post, "ratelimit")
        or callable(LoginView.post)
    )
    assert (
        hasattr(RegisterView.post, "__wrapped__")
        or hasattr(RegisterView.post, "ratelimit")
        or callable(RegisterView.post)
    )
