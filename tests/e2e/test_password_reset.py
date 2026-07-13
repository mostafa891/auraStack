import re

import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from playwright.sync_api import Page


@pytest.mark.django_db(transaction=True)
def test_password_reset_e2e_flow(live_server, page: Page):
    """دورة كاملة لاستعادة كلمة المرور والتأكد من عدم حدوث أي خطأ JSON أو مفتاح غير صالح."""
    User = get_user_model()

    # 1. إنشاء مستخدم نشط في النظام
    email = "reset_e2e@auraflow.com"
    password = "OldPassword123!"
    User.objects.create_user(email=email, password=password)

    page.on("console", lambda msg: print(f"[Browser Console Reset] {msg.text}"))
    page.on("pageerror", lambda err: print(f"[Browser PageError Reset] {err}"))

    # 2. الذهاب لصفحة طلب استعادة كلمة المرور
    page.goto(live_server.url + "/accounts/password/reset/")
    page.wait_for_selector("#email", timeout=5000)

    # 3. إدخال البريد الإلكتروني والإرسال
    page.fill("#email", email)
    page.click("button[type='submit']")

    # 4. التأكد من الوصول لصفحة النجاح
    page.wait_for_url("**/accounts/password/reset/done/", timeout=5000)
    assert page.locator("h1:has-text('Check your email')").is_visible()

    # 5. استخراج رابط الاستعادة من صندوق رسائل دجانغو الافتراضي
    assert len(mail.outbox) == 1
    email_body = mail.outbox[0].body
    print(f"Email Body:\n{email_body}")

    # البحث عن الرابط الذي يحتوي على مفتاح إعادة التعيين
    link_match = re.search(
        r"http://[a-zA-Z0-9\.\-:]+/accounts/password/reset/key/[a-zA-Z0-9\-]+/", email_body
    )
    assert link_match is not None, "Password reset link not found in email body"
    reset_link = link_match.group(0)
    print(f"Parsed Reset Link: {reset_link}")

    # 6. الولوج لرابط الاستعادة وتغيير كلمة المرور
    page.goto(reset_link)
    try:
        page.wait_for_selector("#password", timeout=5000)
    except Exception as e:
        print(f"Current page URL: {page.url}")
        print(f"Current page content: {page.content()}")
        raise e

    # التحقق من أن الاستمارة تظهر دون وجود خطأ الرابط غير صالح
    assert page.locator("h1:has-text('Choose new password')").is_visible()

    page.fill("#password", "NewPassword123!")
    page.fill("#password_confirm", "NewPassword123!")
    page.click("button[type='submit']")

    # 7. التأكد من اكتمال العملية والتوجيه لصفحة النجاح النهائية
    try:
        page.wait_for_url("**/accounts/password/reset/key/done/", timeout=5000)
    except Exception as e:
        print("FAILED AT STEP 7!")
        print(f"Current page URL: {page.url}")
        print(f"Current page content:\n{page.content()}")
        raise e
    assert page.locator("h1:has-text('Password Reset Complete')").is_visible()

    # 8. تجربة تسجيل الدخول بكلمة المرور الجديدة
    page.context.clear_cookies()
    page.goto(live_server.url + "/auth/login/")
    page.wait_for_selector("#email", timeout=5000)
    page.fill("#email", email)
    page.fill("#password", "NewPassword123!")
    page.click("button[type='submit']")

    # التحقق من تسجيل الدخول والتوجه لصفحة البروفايل بنجاح
    page.wait_for_url("**/profile/", timeout=5000)
    assert page.locator("h2:has-text('User Preferences & Settings')").is_visible()
