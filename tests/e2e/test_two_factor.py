import base64
import os
import time

import pytest

# Enable safe environment for async DB access with Playwright
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

from cryptography.hazmat.primitives.hashes import SHA1
from cryptography.hazmat.primitives.twofactor.totp import TOTP
from django.contrib.auth import get_user_model
from playwright.sync_api import Page


def generate_totp_code(secret_b32: str) -> str:
    """Generates 6-digit TOTP code using standard cryptography package."""
    missing_padding = len(secret_b32) % 8
    if missing_padding:
        secret_b32 += "=" * (8 - missing_padding)
    key = base64.b32decode(secret_b32, casefold=True)
    totp = TOTP(key, length=6, time_step=30, algorithm=SHA1())
    return totp.generate(time.time()).decode("utf-8")


@pytest.mark.django_db(transaction=True)
def test_two_factor_activation_and_validation_e2e(live_server, page: Page):
    """End-to-end verification of 2FA TOTP activation, login challenge, and deactivation flows."""
    User = get_user_model()

    # 1. Create active user and login
    email = "mfa_e2e@aurastack.com"
    password = "Password123!"
    User.objects.create_user(email=email, password=password)

    page.on("console", lambda msg: print(f"[Browser Console] {msg.text}"))
    page.on("pageerror", lambda err: print(f"[Browser PageError] {err}"))

    page.goto(live_server.url + "/auth/login/")
    page.wait_for_selector("#email", timeout=5000)
    page.fill("#email", email)
    page.fill("#password", password)
    page.click("button[type='submit']")

    # 2. Visit MFA settings and click activation link
    page.wait_for_url("**/profile/", timeout=5000)
    page.goto(live_server.url + "/auth/mfa/")
    page.wait_for_selector("a:has-text('Set Up 2FA')", timeout=5000)
    page.click("a:has-text('Set Up 2FA')")

    # 3. Access activation page and read secret key
    page.wait_for_url("**/auth/mfa/totp/activate/", timeout=5000)
    assert page.locator("h1:has-text('Enable 2FA')").is_visible()

    secret_key_element = page.locator("code")
    assert secret_key_element.is_visible()
    secret_key = secret_key_element.text_content().strip()
    assert len(secret_key) > 0

    # 4. Generate TOTP code and submit activation form
    totp_code = generate_totp_code(secret_key)
    page.fill("#code", totp_code)
    page.click("button[type='submit']")

    # 5. Verify successful activation and return to MFA dashboard
    page.wait_for_url(lambda url: url.rstrip("/").endswith("/auth/mfa"), timeout=10000)
    page.wait_for_selector("span:has-text('Active')", timeout=5000)
    assert page.locator("span:has-text('Active')").is_visible()

    # 6. Logout and login again to verify TOTP challenge prompt
    page.goto(live_server.url + "/profile/")
    page.wait_for_selector("button:has-text('Logout')", timeout=5000)
    page.click("button:has-text('Logout')")

    page.wait_for_url("**/auth/login/", timeout=5000)
    page.fill("#email", email)
    page.fill("#password", password)
    page.click("button[type='submit']")

    # Verify redirect to 2FA challenge page
    page.wait_for_url("**/accounts/2fa/authenticate/", timeout=5000)
    assert page.locator("h1:has-text('Two-Factor Authentication')").is_visible()

    # Generate new TOTP code and submit
    new_totp_code = generate_totp_code(secret_key)
    page.fill("#code", new_totp_code)
    page.click("button[type='submit']")

    # Verify successful authentication and redirect to profile
    page.wait_for_url("**/profile/", timeout=5000)

    # 7. Deactivate 2FA
    page.goto(live_server.url + "/auth/mfa/")
    page.wait_for_selector("a:has-text('Deactivate')", timeout=5000)
    page.click("a:has-text('Deactivate')")

    page.wait_for_url("**/auth/mfa/totp/deactivate/", timeout=5000)
    assert page.locator("h1:has-text('Deactivate 2FA')").is_visible()

    # Confirm deactivation
    page.fill("#password", password)
    page.click("button[type='submit']")
    page.wait_for_url(lambda url: url.rstrip("/").endswith("/auth/mfa"), timeout=10000)
    page.wait_for_selector("span:has-text('Inactive')", timeout=5000)
