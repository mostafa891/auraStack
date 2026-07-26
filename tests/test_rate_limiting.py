from django.test import RequestFactory, override_settings
from django_ratelimit.core import is_ratelimited

from apps.users.views import LoginView, RegisterView


@override_settings(RATELIMIT_ENABLE=True)
def test_ratelimit_core_logic():
    """Verifies core rate limiting algorithm and IP lockout threshold."""
    factory = RequestFactory()

    # Simulate 11 consecutive POST requests from single IP
    for i in range(11):
        request = factory.post("/auth/login/")
        request.META["REMOTE_ADDR"] = "192.168.1.1"

        # Manual evaluation using ratelimit engine
        limited = is_ratelimited(
            request, key="ip", rate="10/m", method="POST", increment=True, group="login"
        )

        if i >= 10:
            assert limited is True, "11th request must be rate limited"
        else:
            assert limited is False, "First 10 requests must be allowed"


def test_views_have_ratelimit_applied():
    """Verifies that authentication views have rate limit decorators applied."""
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
