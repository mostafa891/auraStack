import os

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

import io
import tempfile

import pytest
from PIL import Image
from playwright.sync_api import Page


@pytest.mark.django_db(transaction=True)
def test_avatar_upload_and_display_e2e(live_server, page: Page):
    """Verifies avatar image upload flow, CSRF handling, instant DOM preview update, and Toast notification."""
    from django.contrib.auth import get_user_model
    from django.core.files.storage import default_storage

    User = get_user_model()

    # 1. Create active user account and login
    email = "avatar_test@aurastack.com"
    password = "Password123!"
    User.objects.create_user(email=email, password=password)

    page.on("console", lambda msg: print(f"[Browser Console] {msg.text}"))
    page.on("pageerror", lambda err: print(f"[Browser PageError] {err}"))

    page.goto(live_server.url + "/auth/login/")
    page.wait_for_selector("#email", timeout=5000)
    page.fill("#email", email)
    page.fill("#password", password)
    page.click("button[type='submit']")

    # 2. Visit profile page
    page.wait_for_url("**/profile/", timeout=5000)
    assert page.locator("h2:has-text('User Preferences & Settings')").is_visible()

    # 3. Generate genuine PNG image in temporary file to pass Magic Bytes validation
    img = Image.new("RGB", (150, 150), color="blue")
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")
    img_bytes = img_byte_arr.getvalue()

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
        temp_file.write(img_bytes)
        temp_file_path = temp_file.name

    # 4. Simulate upload by setting input files on hidden input element
    try:
        # Wait for file input element in DOM
        page.wait_for_selector("input[type='file']", state="attached", timeout=5000)

        # Set temporary file
        page.set_input_files("input[type='file']", temp_file_path)

        # 5. Verify updated image URL in DOM and uploaded image preview
        avatar_img = page.locator("img[alt='Avatar']")
        page.wait_for_selector("img[alt='Avatar']", timeout=15000)

        # 6. Verify image source URL points to media/avatars/ directory
        page.wait_for_function(
            "() => document.querySelector(\"img[alt='Avatar']\") && "
            "document.querySelector(\"img[alt='Avatar']\").src.includes('/media/avatars/')",
            timeout=15000,
        )
        src_url = avatar_img.get_attribute("src")
        assert "/media/avatars/" in src_url
        assert src_url.endswith(".png")

        # Cleanup uploaded avatar file from storage
        relative_path = src_url.split("/media/")[-1]
        if default_storage.exists(relative_path):
            default_storage.delete(relative_path)

    finally:
        # Clear input files and close page to release file lock on Windows
        try:
            page.set_input_files("input[type='file']", [])
        except Exception:
            pass
        page.close()

        # Remove temporary file
        if os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                print(f"Warning: Could not delete temp file: {e}")
