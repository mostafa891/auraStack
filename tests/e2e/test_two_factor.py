import base64
import os
import time

import pytest

# تفعيل البيئة الآمنة للاستدعاء غير المتزامن لقاعدة البيانات مع Playwright
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

from cryptography.hazmat.primitives.hashes import SHA1
from cryptography.hazmat.primitives.twofactor.totp import TOTP
from django.contrib.auth import get_user_model
from playwright.sync_api import Page


def generate_totp_code(secret_b32: str) -> str:
    """توليد كود الـ TOTP ذي الـ 6 أرقام باستخدام حزمة cryptography القياسية."""
    # تطبيع وحشو السلسلة بالـ = لتفادي أخطاء الطول في الـ base32
    missing_padding = len(secret_b32) % 8
    if missing_padding:
        secret_b32 += "=" * (8 - missing_padding)
    key = base64.b32decode(secret_b32, casefold=True)
    totp = TOTP(key, length=6, time_step=30, algorithm=SHA1())
    return totp.generate(time.time()).decode("utf-8")


@pytest.mark.django_db(transaction=True)
def test_two_factor_activation_and_validation_e2e(live_server, page: Page):
    """التحقق من تفعيل التحقق الثنائي (2FA)، تسجيل الخروج، طلب الرمز أثناء الدخول، ثم التعطيل."""
    User = get_user_model()

    # 1. إنشاء مستخدم نشط وتسجيل الدخول
    email = "mfa_e2e@auraflow.com"
    password = "Password123!"
    User.objects.create_user(email=email, password=password)

    page.on("console", lambda msg: print(f"[Browser Console] {msg.text}"))
    page.on("pageerror", lambda err: print(f"[Browser PageError] {err}"))

    page.goto(live_server.url + "/auth/login/")
    page.wait_for_selector("#email", timeout=5000)
    page.fill("#email", email)
    page.fill("#password", password)
    page.click("button[type='submit']")

    # 2. التوجه لصفحة الـ MFA والضغط على رابط التفعيل
    page.wait_for_url("**/profile/", timeout=5000)
    page.goto(live_server.url + "/auth/mfa/")
    page.wait_for_selector("a:has-text('Set Up 2FA')", timeout=5000)
    page.click("a:has-text('Set Up 2FA')")

    # 3. الوصول لصفحة التفعيل واستخراج الرمز السري من الواجهة
    page.wait_for_url("**/auth/mfa/totp/activate/", timeout=5000)
    assert page.locator("h1:has-text('Enable 2FA')").is_visible()

    # قراءة الرمز السري المكتوب في الصفحة
    secret_key_element = page.locator("code")
    assert secret_key_element.is_visible()
    secret_key = secret_key_element.text_content().strip()
    assert len(secret_key) > 0

    # 4. توليد كود الـ TOTP وتعبئته لتفعيل الخدمة
    totp_code = generate_totp_code(secret_key)
    page.fill("#code", totp_code)
    page.click("button[type='submit']")

    # 5. التأكد من النجاح والعودة لقائمة الـ MFA وحالة TOTP نشطة
    page.wait_for_url("**/auth/mfa/", timeout=5000)
    assert page.locator("span:has-text('Active /')").is_visible()

    # 6. تسجيل الخروج وإعادة الدخول للتحقق من طلب الرمز
    page.goto(live_server.url + "/profile/")
    page.wait_for_selector("button:has-text('Logout')", timeout=5000)
    page.click("button:has-text('Logout')")

    page.wait_for_url("**/auth/login/", timeout=5000)
    page.fill("#email", email)
    page.fill("#password", password)
    page.click("button[type='submit']")

    # التحقق من توجيه المستخدم لصفحة المطالبة بكود التحقق الثنائي
    page.wait_for_url("**/accounts/2fa/authenticate/", timeout=5000)
    assert page.locator("h1:has-text('Two-Factor Authentication')").is_visible()

    # توليد رمز جديد وكتابته
    new_totp_code = generate_totp_code(secret_key)
    page.fill("#code", new_totp_code)
    page.click("button[type='submit']")

    # التحقق من اكتمال الدخول والتوجه للبروفايل
    page.wait_for_url("**/profile/", timeout=5000)

    # 7. تعطيل الخدمة مجدداً
    page.goto(live_server.url + "/auth/mfa/")
    page.wait_for_selector("a:has-text('Deactivate')", timeout=5000)
    page.click("a:has-text('Deactivate')")

    page.wait_for_url("**/auth/mfa/totp/deactivate/", timeout=5000)
    assert page.locator("h1:has-text('Deactivate 2FA')").is_visible()

    # تأكيد التعطيل
    page.fill("#password", password)
    page.click("button[type='submit']")
    page.wait_for_url("**/auth/mfa/", timeout=5000)
    page.wait_for_selector("span:has-text('Inactive /')", timeout=5000)
