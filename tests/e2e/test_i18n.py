import pytest
from django.contrib.auth import get_user_model
from playwright.sync_api import Page


@pytest.mark.django_db(transaction=True)
def test_i18n_and_direction_flipping_e2e(live_server, page: Page):
    """التحقق من عمل المترجم التفاعلي وتعديل اتجاهات الصفحة (RTL/LTR) تلقائياً."""
    User = get_user_model()

    page.on("console", lambda msg: print(f"[Browser Console i18n] {msg.text}"))
    page.on("pageerror", lambda err: print(f"[Browser PageError i18n] {err}"))

    # 1. زيارة صفحة الدخول (تظهر بالإنجليزية افتراضياً)
    page.goto(live_server.url + "/auth/login/")
    try:
        page.wait_for_selector("#email", timeout=5000)
    except Exception as e:
        print(f"Current page URL: {page.url}")
        print(f"Current page content: {page.content()}")
        raise e

    # التحقق من أن اتجاه الصفحة الافتراضي هو LTR واللغة en
    assert page.locator("html").get_attribute("dir") == "ltr"
    assert page.locator("html").get_attribute("lang") == "en"
    assert page.locator("h1:has-text('Welcome back')").is_visible()

    # 2. الضغط على زر تبديل اللغة للعربية
    page.click("button:has-text('العربية')")
    page.wait_for_function("document.documentElement.lang === 'ar'", timeout=5000)

    # التحقق من انقلاب الاتجاه إلى RTL وتغير اللغة إلى ar والنصوص للعربية
    assert page.locator("html").get_attribute("dir") == "rtl"
    assert page.locator("html").get_attribute("lang") == "ar"
    assert page.locator("h1:has-text('مرحباً بك مجدداً')").is_visible()

    # 3. الضغط للتبديل مرة أخرى للإنجليزية
    page.click("button:has-text('English')")
    page.wait_for_function("document.documentElement.lang === 'en'", timeout=5000)

    # التحقق من العودة لـ LTR واللغة en
    assert page.locator("html").get_attribute("dir") == "ltr"
    assert page.locator("html").get_attribute("lang") == "en"

    # 4. إنشاء مستخدم وتجربة تسجيل الدخول وتغيير التفضيلات
    email = "i18n_user@auraflow.com"
    User.objects.create_user(email=email, password="Password123!")

    page.fill("#email", email)
    page.fill("#password", "Password123!")
    page.click("button[type='submit']")

    page.wait_for_url("**/profile/", timeout=5000)

    # التحقق من أن التفضيلات تظهر وتغيير اللغة للعربية وحفظها
    page.select_option("#language", "ar")
    page.click("button:has-text('Save Settings')")
    page.wait_for_function("document.documentElement.lang === 'ar'", timeout=5000)

    # التحقق من حفظ التفضيلات وتحديث اتجاه الصفحة إلى RTL
    assert page.locator("html").get_attribute("dir") == "rtl"
    assert page.locator("html").get_attribute("lang") == "ar"

    # إعادة تحميل الصفحة للتحقق من قراءة التفضيلات المخزنة في قاعدة البيانات تلقائياً
    page.reload()
    page.wait_for_selector("#language", timeout=5000)
    assert page.locator("html").get_attribute("dir") == "rtl"
    assert page.locator("html").get_attribute("lang") == "ar"
