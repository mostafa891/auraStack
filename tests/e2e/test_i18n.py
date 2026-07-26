import pytest
from django.contrib.auth import get_user_model
from playwright.sync_api import Page


@pytest.mark.django_db(transaction=True)
def test_i18n_and_direction_flipping_e2e(live_server, page: Page):
    """End-to-end testing of dynamic internationalization (i18n) and RTL/LTR direction flipping."""
    User = get_user_model()

    page.on("console", lambda msg: print(f"[Browser Console i18n] {msg.text}"))
    page.on("pageerror", lambda err: print(f"[Browser PageError i18n] {err}"))

    # 1. Visit login page (default LTR / English)
    page.goto(live_server.url + "/auth/login/")
    page.wait_for_selector("#email", timeout=5000)

    # Verify default page direction is LTR and lang is en
    assert page.locator("html").get_attribute("dir") == "ltr"
    assert page.locator("html").get_attribute("lang") == "en"
    assert page.locator("h1:has-text('Welcome back')").is_visible()

    # 2. Click language switcher to Arabic
    page.click("button:has-text('العربية')")
    page.wait_for_function("document.documentElement.lang === 'ar'", timeout=5000)

    # Verify direction flipped to RTL and lang is ar
    assert page.locator("html").get_attribute("dir") == "rtl"
    assert page.locator("html").get_attribute("lang") == "ar"
    assert page.locator("h1:has-text('مرحباً بك مجدداً')").is_visible()

    # 3. Switch back to English
    page.click("button:has-text('English')")
    page.wait_for_function("document.documentElement.lang === 'en'", timeout=5000)

    # Verify return to LTR and lang en
    assert page.locator("html").get_attribute("dir") == "ltr"
    assert page.locator("html").get_attribute("lang") == "en"

    # 4. Create user account, login, and update user language preference in profile
    email = "i18n_user@aurastack.com"
    User.objects.create_user(email=email, password="Password123!")

    page.fill("#email", email)
    page.fill("#password", "Password123!")
    page.click("button[type='submit']")

    page.wait_for_url("**/profile/", timeout=5000)

    # Select Arabic preference and save settings
    page.select_option("#language", "ar")
    page.click("button:has-text('Save Settings')")
    page.wait_for_function("document.documentElement.lang === 'ar'", timeout=5000)

    # Verify direction flipped to RTL
    assert page.locator("html").get_attribute("dir") == "rtl"
    assert page.locator("html").get_attribute("lang") == "ar"

    # Reload page to verify saved user preference persists from DB
    page.reload()
    page.wait_for_selector("#language", timeout=5000)
    assert page.locator("html").get_attribute("dir") == "rtl"
    assert page.locator("html").get_attribute("lang") == "ar"
