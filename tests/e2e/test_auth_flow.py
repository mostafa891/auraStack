import pytest
from playwright.sync_api import Page


@pytest.mark.django_db(transaction=True)
def test_auth_and_preferences_flow(live_server, page: Page):
    """اختبار E2E شامل لدورة التسجيل، تحديث المظهر، تسجيل الخروج، وتغيير السمة بصرياً."""

    # 1. التوجه لصفحة التسجيل
    page.on("console", lambda msg: print(f"[Browser Console] {msg.text}"))
    page.on("pageerror", lambda err: print(f"[Browser PageError] {err}"))

    try:
        page.goto(live_server.url + "/auth/register/")
    except Exception as e:
        print(f"Navigation failed: {e}")
        print(f"Page content: {page.content()}")
        raise e

    # 2. تعبئة البيانات وإرسال الفورم
    try:
        page.wait_for_selector("#email", timeout=5000)
    except Exception as e:
        print(f"Selector #email timed out. Current page URL: {page.url}")
        print(f"Page content: {page.content()}")
        raise e

    page.fill("#email", "e2e_user@auraflow.com")
    page.fill("#password", "Password123!")
    page.fill("#password_confirm", "Password123!")
    page.click("button[type='submit']")

    # 3. التأكد من تحويل المستخدم تلقائياً لصفحة التفضيلات والملف الشخصي
    try:
        page.wait_for_url("**/profile/", timeout=5000)
    except Exception as e:
        print(f"Redirect to /profile/ failed. Current URL: {page.url}")
        print(f"Page content: {page.content()}")
        raise e

    # التحقق من وجود نصوص لوحة الإعدادات
    assert page.locator("h2:has-text('User Preferences & Settings')").is_visible()

    # 4. تحديث المظهر للمظهر الداكن (Dark Mode) وحفظ التفضيلات
    page.select_option("#theme", "DARK")
    page.click("button:has-text('Save Preferences')")

    # انتظار التحديث وحفظ قاعدة البيانات
    page.wait_for_timeout(1000)

    # التحقق من تفعيل المظهر الداكن بصرياً في المتصفح عبر فحص كلاس dark
    dark_class_exists = page.evaluate("() => document.documentElement.classList.contains('dark')")
    assert dark_class_exists is True

    # 5. تسجيل الخروج والتأكد من العودة لصفحة الدخول
    page.click("button:has-text('Logout')")
    page.wait_for_url("**/auth/login/")
    assert page.locator("h1:has-text('Welcome back')").is_visible()
