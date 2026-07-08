import pytest

from apps.users.models import CustomUser


@pytest.mark.django_db
def test_create_user_successful():
    """التحقق من نجاح إنشاء مستخدم اعتيادي وحفظ كلمته مشفرة."""
    user = CustomUser.objects.create_user(
        email="newuser@auraflow.com",
        password="SecurePassword123!",
        first_name="First",
        last_name="Last",
    )
    assert user.email == "newuser@auraflow.com"
    assert user.check_password("SecurePassword123!") is True
    assert user.is_staff is False
    assert user.is_superuser is False
    assert str(user) == "First Last <newuser@auraflow.com>"


@pytest.mark.django_db
def test_create_user_missing_email_raises_value_error():
    """التحقق من إطلاق ValueError عند محاولة إنشاء مستخدم بدون بريد."""
    with pytest.raises(ValueError, match="The Email field must be set"):
        CustomUser.objects.create_user(email="")


@pytest.mark.django_db
def test_create_superuser_successful():
    """التحقق من تفعيل صلاحيات الإدارة الكاملة للمستخدم الخارق."""
    superuser = CustomUser.objects.create_superuser(
        email="admin@auraflow.com",
        password="AdminPassword123!",
    )
    assert superuser.email == "admin@auraflow.com"
    assert superuser.is_staff is True
    assert superuser.is_superuser is True
    assert superuser.is_active is True
