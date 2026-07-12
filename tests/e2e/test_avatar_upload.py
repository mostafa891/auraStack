import os

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

import io
import tempfile

import pytest
from PIL import Image
from playwright.sync_api import Page


@pytest.mark.django_db(transaction=True)
def test_avatar_upload_and_display_e2e(live_server, page: Page):
    """التحقق من رفع صورة الملف الشخصي بنجاح، وتمرير الـ CSRF، وتحديث العرض الفوري والـ Toast."""
    from django.contrib.auth import get_user_model
    from django.core.files.storage import default_storage

    User = get_user_model()

    # 1. إنشاء حساب وتجربة تسجيل الدخول
    email = "avatar_test@auraflow.com"
    password = "Password123!"
    User.objects.create_user(email=email, password=password)

    page.on("console", lambda msg: print(f"[Browser Console] {msg.text}"))
    page.on("pageerror", lambda err: print(f"[Browser PageError] {err}"))

    page.goto(live_server.url + "/auth/login/")
    page.wait_for_selector("#email", timeout=5000)
    page.fill("#email", email)
    page.fill("#password", password)
    page.click("button[type='submit']")

    # 2. الذهاب لصفحة الملف الشخصي
    page.wait_for_url("**/profile/", timeout=5000)
    assert page.locator("h2:has-text('User Preferences & Settings')").is_visible()

    # 3. توليد صورة PNG حقيقية في ملف مؤقت لمطابقة فحص الـ Magic Bytes
    img = Image.new("RGB", (150, 150), color="blue")
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")
    img_bytes = img_byte_arr.getvalue()

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
        temp_file.write(img_bytes)
        temp_file_path = temp_file.name

    # 4. محاكاة الرفع عن طريق تعيين الملف في حقل الإدخال المخفي
    try:
        # الانتظار حتى استقرار الصفحة وجاهزية الإدخال
        page.wait_for_selector("input[type='file']", state="attached", timeout=5000)

        # تعيين الملف المؤقت للرفع
        page.set_input_files("input[type='file']", temp_file_path)

        # 5. التحقق من ظهور التنبيه (Toast) بنجاح الرفع باللغة الافتراضية
        page.wait_for_selector("text=Avatar uploaded successfully!", timeout=5000)

        # 6. التحقق من تحديث رابط الصورة في الـ DOM وظهور الصورة المرفوعة
        avatar_img = page.locator("img[alt='Avatar']")
        page.wait_for_selector("img[alt='Avatar']", timeout=5000)

        src_url = avatar_img.get_attribute("src")
        assert "/media/avatars/" in src_url
        assert src_url.endswith(".png")

        # تنظيف الملف المرفوع في نظام تخزين دجانغو لتجنب تراكم الملفات المهملة
        # استخراج مسار الملف النسبي من الرابط المولد
        relative_path = src_url.split("/media/")[-1]
        if default_storage.exists(relative_path):
            default_storage.delete(relative_path)

    finally:
        # مسح حقل الإدخال وإغلاق الصفحة لتحرير قفل الملف في متصفح Chromium على نظام ويندوز
        try:
            page.set_input_files("input[type='file']", [])
        except Exception:
            pass
        page.close()

        # إزالة الملف المؤقت من النظام
        if os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                print(f"Warning: Could not delete temp file: {e}")
