import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_login_page_renders_successful(client):
    """التحقق من تحميل صفحة تسجيل الدخول بنجاح."""
    response = client.get(reverse("auth:login"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_register_page_renders_successful(client):
    """التحقق من تحميل صفحة إنشاء الحساب بنجاح."""
    response = client.get(reverse("auth:register"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_profile_page_redirects_anonymous(client):
    """التحقق من حماية التفضيلات وتوجيه غير المصادقين لصفحة الدخول."""
    response = client.get(reverse("profile"))
    assert response.status_code == 302
    assert reverse("auth:login") in response.url


@pytest.mark.django_db
def test_profile_page_renders_authenticated(client, test_user):
    """التحقق من وصول المستخدم المصادق لصفحة الملف الشخصي بنجاح."""
    client.force_login(test_user)
    response = client.get(reverse("profile"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_logout_redirects_to_login(client, test_user):
    """التحقق من نجاح تسجيل الخروج وإبطال الجلسة."""
    client.force_login(test_user)
    response = client.post(reverse("auth:logout"))
    assert response.status_code == 302
    assert reverse("auth:login") in response.url


@pytest.mark.django_db
def test_profile_update_preferences(client, test_user):
    """التحقق من تحديث تفضيلات المستخدم وحفظها في قاعدة البيانات."""
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
    # التحقق من تحديث الكائن
    test_user.refresh_from_db()
    assert test_user.language == "ar"
    assert test_user.theme == "DARK"
    assert test_user.timezone == "Asia/Riyadh"
