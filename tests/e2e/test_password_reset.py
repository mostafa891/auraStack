import re

import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from playwright.sync_api import Page


@pytest.mark.django_db(transaction=True)
def test_password_reset_e2e_flow(live_server, page: Page):
    """End-to-end testing of password reset flow: request, email token extraction, key validation, and login."""
    User = get_user_model()

    # 1. Create active user
    email = "reset_e2e@aurastack.com"
    password = "OldPassword123!"
    User.objects.create_user(email=email, password=password)

    page.on("console", lambda msg: print(f"[Browser Console Reset] {msg.text}"))
    page.on("pageerror", lambda err: print(f"[Browser PageError Reset] {err}"))

    # 2. Visit password reset request page
    page.goto(live_server.url + "/accounts/password/reset/")
    page.wait_for_selector("#email", timeout=5000)

    # 3. Submit email
    page.fill("#email", email)
    page.click("button[type='submit']")

    # 4. Verify redirect to request done page
    page.wait_for_url("**/accounts/password/reset/done/", timeout=5000)
    assert page.locator("h1:has-text('Check your email')").is_visible()

    # 5. Extract reset link from outbox email
    assert len(mail.outbox) == 1
    email_body = mail.outbox[0].body

    link_match = re.search(
        r"http://[a-zA-Z0-9\.\-:]+/accounts/password/reset/key/[a-zA-Z0-9\-]+/", email_body
    )
    assert link_match is not None, "Password reset link not found in email body"
    reset_link = link_match.group(0)

    # 6. Visit reset link and submit new password
    page.goto(reset_link)
    page.wait_for_selector("#password", timeout=5000)
    assert page.locator("h1:has-text('Choose new password')").is_visible()

    page.fill("#password", "NewPassword123!")
    page.fill("#password_confirm", "NewPassword123!")
    page.click("button[type='submit']")

    # 7. Verify redirect to reset completion page
    page.wait_for_url("**/accounts/password/reset/key/done/", timeout=5000)
    assert page.locator("h1:has-text('Password Reset Complete')").is_visible()

    # 8. Test login with new password
    page.context.clear_cookies()
    page.goto(live_server.url + "/auth/login/")
    page.wait_for_selector("#email", timeout=5000)
    page.fill("#email", email)
    page.fill("#password", "NewPassword123!")
    page.click("button[type='submit']")

    # Verify successful login and redirect to profile
    page.wait_for_url("**/profile/", timeout=5000)
    assert page.locator("h2:has-text('User Preferences & Settings')").is_visible()
