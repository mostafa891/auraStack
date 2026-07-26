import pytest
from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpResponseRedirect
from django.test import RequestFactory

from apps.users.adapters.allauth import CustomAccountAdapter
from apps.users.views_security import SetLanguageView


@pytest.mark.django_db
def test_custom_account_adapter_is_ajax():
    """Verifies custom account adapter disables AJAX detection when Inertia headers are present."""
    factory = RequestFactory()
    adapter = CustomAccountAdapter()

    # 1. Standard AJAX request
    request_ajax = factory.post("/accounts/login/", HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    assert adapter.is_ajax(request_ajax) is True

    # 2. Inertia SPA request (must NOT be treated as legacy AJAX to receive proper Inertia response)
    request_inertia = factory.post("/accounts/login/", HTTP_X_INERTIA="true")
    assert adapter.is_ajax(request_inertia) is False

    # 3. Inertia request with explicit header
    request_inertia_header = factory.post("/accounts/login/", HTTP_X_INERTIA="true")
    assert adapter.is_ajax(request_inertia_header) is False

    # 4. Standard non-AJAX request
    request_normal = factory.post("/accounts/login/")
    assert adapter.is_ajax(request_normal) is False


@pytest.mark.django_db
def test_set_language_view():
    """Verifies SetLanguageView updates language preference in session and cookies."""
    factory = RequestFactory()
    view = SetLanguageView.as_view()

    # 1. POST request to switch language to Arabic
    request = factory.post(
        "/auth/set-language/", data={"language": "ar"}, content_type="application/json"
    )

    # Attach session middleware mock
    middleware = SessionMiddleware(lambda req: None)
    middleware.process_request(request)
    request.session.save()

    response = view(request)

    # Verify redirect response
    assert response.status_code == 302

    # Verify cookie and session updates
    assert response.cookies[settings.LANGUAGE_COOKIE_NAME].value == "ar"
    assert request.session["_language"] == "ar"


@pytest.mark.django_db
def test_mock_oauth_login(client):
    """Mocks successful OAuth login flow (Google / GitHub) to verify django-allauth integration."""
    from unittest.mock import patch

    import allauth.socialaccount.helpers as helpers
    from allauth.socialaccount.models import SocialLogin
    from django.contrib.auth import get_user_model

    User = get_user_model()

    user = User.objects.create_user(email="oauth_test@example.com", password="Password123!")
    social_login = SocialLogin(user=user)

    with patch("allauth.socialaccount.helpers.complete_social_login") as mock_complete:
        mock_complete.return_value = HttpResponseRedirect(redirect_to="/profile/")

        request = RequestFactory().get("/accounts/google/login/callback/")
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        request.user = user

        response = helpers.complete_social_login(request, social_login)

        assert response.status_code == 302
        assert response["Location"] == "/profile/"


@pytest.mark.django_db
def test_avatar_delete_view(client):
    """Verifies avatar deletion clears user avatar_url."""
    from django.contrib.auth import get_user_model

    User = get_user_model()
    user = User.objects.create_user(
        email="avatar_delete@example.com",
        password="Password123!",
        avatar_url="http://localhost:8000/media/avatars/test.png",
    )
    client.force_login(user)

    response = client.post("/auth/profile/avatar/delete/")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

    user.refresh_from_db()
    assert user.avatar_url == ""
