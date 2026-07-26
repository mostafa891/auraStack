import pytest
from playwright.sync_api import Page


@pytest.mark.django_db(transaction=True)
def test_auth_and_preferences_flow(live_server, page: Page):
    """End-to-end testing of user registration, profile preference updates, dark mode toggle, and logout."""

    # 1. Navigate to registration page
    page.on("console", lambda msg: print(f"[Browser Console] {msg.text}"))
    page.on("pageerror", lambda err: print(f"[Browser PageError] {err}"))

    page.goto(live_server.url + "/auth/register/")
    page.wait_for_selector("#email", timeout=5000)

    # 2. Fill credentials and submit registration form
    page.fill("#email", "e2e_user@aurastack.com")
    page.fill("#password", "Password123!")
    page.fill("#password_confirm", "Password123!")
    page.click("button[type='submit']")

    # 3. Verify auto-redirect to profile preferences page
    page.wait_for_url("**/profile/", timeout=5000)
    assert page.locator("h2:has-text('User Preferences & Settings')").is_visible()

    # 4. Update theme preference to DARK and save settings
    page.select_option("#theme", "DARK")
    page.click("button:has-text('Save Settings')")
    page.wait_for_timeout(1000)

    # Verify dark mode class added to DOM root element
    dark_class_exists = page.evaluate("() => document.documentElement.classList.contains('dark')")
    assert dark_class_exists is True

    # 5. Logout and verify redirect to login page
    page.click("button:has-text('Logout')")
    page.wait_for_url("**/auth/login/")
    assert page.locator("h1:has-text('Welcome back')").is_visible()
