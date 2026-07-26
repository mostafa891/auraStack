import pytest

from apps.users.models import CustomUser


@pytest.mark.django_db
def test_create_user_successful():
    """Verifies successful creation of standard user with hashed password."""
    user = CustomUser.objects.create_user(
        email="newuser@aurastack.com",
        password="SecurePassword123!",
        first_name="First",
        last_name="Last",
    )
    assert user.email == "newuser@aurastack.com"
    assert user.check_password("SecurePassword123!") is True
    assert user.is_staff is False
    assert user.is_superuser is False
    assert str(user) == "First Last <newuser@aurastack.com>"


@pytest.mark.django_db
def test_create_user_missing_email_raises_value_error():
    """Verifies ValueError is raised when attempting to create a user without email."""
    with pytest.raises(ValueError, match="The Email field must be set"):
        CustomUser.objects.create_user(email="")


@pytest.mark.django_db
def test_create_superuser_successful():
    """Verifies superuser creation with admin permissions enabled."""
    superuser = CustomUser.objects.create_superuser(
        email="admin@aurastack.com",
        password="AdminPassword123!",
    )
    assert superuser.email == "admin@aurastack.com"
    assert superuser.is_staff is True
    assert superuser.is_superuser is True
    assert superuser.is_active is True
