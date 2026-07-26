import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_login_page_renders_successful(client):
    """Verifies successful loading of login page."""
    response = client.get(reverse("auth:login"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_register_page_renders_successful(client):
    """Verifies successful loading of registration page."""
    response = client.get(reverse("auth:register"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_profile_page_redirects_anonymous(client):
    """Verifies unauthorized users are redirected to login."""
    response = client.get(reverse("profile"))
    assert response.status_code == 302
    assert reverse("auth:login") in response.url


@pytest.mark.django_db
def test_profile_page_renders_authenticated(client, test_user):
    """Verifies authenticated user access to profile page."""
    client.force_login(test_user)
    response = client.get(reverse("profile"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_logout_redirects_to_login(client, test_user):
    """Verifies logout invalidates session and redirects to login."""
    client.force_login(test_user)
    response = client.post(reverse("auth:logout"))
    assert response.status_code == 302
    assert reverse("auth:login") in response.url


@pytest.mark.django_db
def test_profile_update_preferences(client, test_user):
    """Verifies updating user preferences in database."""
    client.force_login(test_user)
    response = client.post(
        reverse("auth:profile_update"),
        data={
            "language": "ar",
            "theme": "DARK",
            "timezone": "Asia/Riyadh",
        },
    )
    assert response.status_code == 302
    # Verify model update
    test_user.refresh_from_db()
    assert test_user.language == "ar"
    assert test_user.theme == "DARK"
    assert test_user.timezone == "Asia/Riyadh"


# ==============================================================================
# Security Views Tests (MFA, Password Change)
# ==============================================================================


@pytest.mark.django_db
def test_password_change_page_redirects_anonymous(client):
    """Verifies password change page protection for anonymous users."""
    response = client.get(reverse("auth:password_change"))
    assert response.status_code == 302


@pytest.mark.django_db
def test_password_change_page_renders_authenticated(client, test_user):
    """Verifies password change page rendering for authenticated users."""
    client.force_login(test_user)
    response = client.get(reverse("auth:password_change"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_password_change_successful(client, test_user):
    """Verifies successful password change for authenticated user."""
    # Set known test password to refresh database hash
    test_user.set_password("OldPass123!")
    test_user.save()

    # Log in after setting password to match session hash
    client.force_login(test_user)

    response = client.post(
        reverse("auth:password_change"),
        data={
            "old_password": "OldPass123!",
            "password": "NewSecurePass123!",
            "password_confirm": "NewSecurePass123!",
        },
    )
    assert response.status_code == 302
    assert response.url == reverse("profile")

    # Verify password updated in database
    test_user.refresh_from_db()
    assert test_user.check_password("NewSecurePass123!")


@pytest.mark.django_db
def test_mfa_list_view_renders_authenticated(client, test_user):
    """Verifies MFA settings page rendering for authenticated user."""
    client.force_login(test_user)
    response = client.get(reverse("auth:mfa_list"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_totp_activate_view_renders_authenticated(client, test_user):
    """Verifies TOTP activation page rendering for authenticated user."""
    client.force_login(test_user)
    response = client.get(reverse("auth:totp_activate"))
    assert response.status_code == 200
    # Ensure TOTP secret saved in session
    assert "totp_secret" in client.session
