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


# ==============================================================================
# Security Views Tests (MFA, Password Change)
# ==============================================================================


@pytest.mark.django_db
def test_password_change_page_redirects_anonymous(client):
    """التحقق من حماية صفحة تغيير كلمة المرور للمستخدمين المجهولين."""
    response = client.get(reverse("auth:password_change"))
    assert response.status_code == 302


@pytest.mark.django_db
def test_password_change_page_renders_authenticated(client, test_user):
    """التحقق من تحميل صفحة تغيير كلمة المرور للمستخدم المصادق."""
    client.force_login(test_user)
    response = client.get(reverse("auth:password_change"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_password_change_successful(client, test_user):
    """التحقق من نجاح تغيير كلمة المرور للمستخدم المصادق."""
    # تعيين كلمة مرور تجريبية معروفة أولاً لتحديث الـ hash في قاعدة البيانات
    test_user.set_password("OldPass123!")
    test_user.save()

    # تسجيل الدخول بعد تعيين كلمة المرور لكي تتوافق بصمة الـ Session مع الباك إند
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

    # التحقق من أن كلمة المرور تغيرت فعلياً
    test_user.refresh_from_db()
    assert test_user.check_password("NewSecurePass123!")


@pytest.mark.django_db
def test_mfa_list_view_renders_authenticated(client, test_user):
    """التحقق من تحميل صفحة قائمة الـ MFA للمستخدم المصادق."""
    client.force_login(test_user)
    response = client.get(reverse("auth:mfa_list"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_totp_activate_view_renders_authenticated(client, test_user):
    """التحقق من تحميل صفحة تفعيل الـ TOTP للمستخدم المصادق."""
    client.force_login(test_user)
    response = client.get(reverse("auth:totp_activate"))
    assert response.status_code == 200
    # التأكد من حفظ الـ secret في الجلسة لمطابقتها لاحقاً
    assert "totp_secret" in client.session
