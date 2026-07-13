import pytest
from django.contrib.auth import get_user_model
from playwright.sync_api import Page

from apps.teams.models import WorkspaceInvitation


@pytest.mark.django_db(transaction=True)
def test_workspace_permissions_and_invite_acceptance_e2e(live_server, page: Page):
    """التحقق من صلاحيات الأدوار المختلفة (Owner, Admin, Member) وسير قبول الدعوة بنجاح."""
    User = get_user_model()

    # 1. إنشاء حساب المالك (Owner) ومساحة العمل Acme Corp
    owner_email = "owner_perm@auraflow.com"
    owner_password = "Password123!"
    User.objects.create_user(email=owner_email, password=owner_password)

    page.on("console", lambda msg: print(f"[Browser Console Perm] {msg.text}"))
    page.on("pageerror", lambda err: print(f"[Browser PageError Perm] {err}"))

    page.goto(live_server.url + "/auth/login/")
    page.wait_for_selector("#email", timeout=5000)
    page.fill("#email", owner_email)
    page.fill("#password", owner_password)
    page.click("button[type='submit']")

    page.wait_for_url("**/profile/", timeout=5000)
    page.click("a:has-text('Manage Workspaces')")

    page.wait_for_url("**/workspaces/", timeout=5000)
    page.click("button:has-text('Create Workspace')")
    page.wait_for_selector("#modal-name", timeout=2000)
    page.fill("#modal-name", "Acme Corp")
    page.click("button[type='submit']:has-text('Create Workspace')")

    # انتظار التوجيه لصفحة إعدادات مساحة العمل
    page.wait_for_url("**/workspaces/acme-corp/settings/", timeout=5000)
    assert page.locator("h1", has_text="Acme Corp").is_visible()

    # 2. دعوة عضو جديد برتبة MEMBER
    member_email = "member_perm@auraflow.com"
    page.fill("#invite-email", member_email)
    page.select_option("#invite-role", "MEMBER")
    page.click("button:has-text('Send Invitation')")

    # انتظر ظهور الدعوة المعلقة
    page.wait_for_selector(f"[title='{member_email}']", timeout=5000)

    # 3. استخراج التوكن من قاعدة البيانات ومحاكاة التسجيل وقبول الدعوة للعضو الجديد
    invitation = WorkspaceInvitation.objects.get(email=member_email)
    invite_token = str(invitation.token)

    # تسجيل خروج المالك
    page.goto(live_server.url + "/profile/")
    page.click("button:has-text('Logout')")
    page.wait_for_url("**/auth/login/", timeout=5000)

    # إنشاء حساب العضو المدعو أولاً (لتسجيل دخوله)
    member_password = "Password123!"
    User.objects.create_user(email=member_email, password=member_password)

    # تسجيل دخول العضو
    page.fill("#email", member_email)
    page.fill("#password", member_password)
    page.click("button[type='submit']")
    page.wait_for_url("**/profile/", timeout=5000)

    # الذهاب لرابط قبول الدعوة المباشر
    page.goto(live_server.url + f"/workspaces/invitations/{invite_token}/accept/")

    # التحقق من قبول الدعوة والتوجيه التلقائي لصفحة الإعدادات
    page.wait_for_url("**/workspaces/acme-corp/settings/", timeout=5000)
    assert page.locator("h1", has_text="Acme Corp").is_visible()
    assert page.locator("span:has-text(': MEMBER')").is_visible()

    # 4. التحقق من أن صلاحيات الـ MEMBER مقيدة (لا يمكن تعديل الحقول)
    name_input = page.locator("#name")
    assert name_input.is_disabled()
    slug_input = page.locator("#slug")
    assert slug_input.is_disabled()

    # التحقق من أن استمارة إرسال الدعوة غير مرئية أو مخفية لغير المدراء
    assert not page.locator("#invite-email").is_visible()

    # 5. ترقية العضو إلى رتبة ADMIN من قبل المالك
    # تسجيل خروج العضو
    page.goto(live_server.url + "/profile/")
    page.click("button:has-text('Logout')")
    page.wait_for_url("**/auth/login/", timeout=5000)

    # تسجيل دخول المالك
    page.fill("#email", owner_email)
    page.fill("#password", owner_password)
    page.click("button[type='submit']")
    page.wait_for_url("**/profile/", timeout=5000)

    # الذهاب للإعدادات وترقية العضو
    page.goto(live_server.url + "/workspaces/acme-corp/settings/")
    page.wait_for_selector("select", timeout=5000)

    # تحديد خيار الترقية لـ ADMIN للعضو الآخر (وليس لنفسه)
    page.locator(f"tr:has-text('{member_email}') select").select_option("ADMIN")
    page.wait_for_timeout(1000)  # انتظار حفظ البيانات تلقائياً من الـ change event

    # تسجيل خروج المالك مجدداً
    page.goto(live_server.url + "/profile/")
    page.click("button:has-text('Logout')")
    page.wait_for_url("**/auth/login/", timeout=5000)

    # تسجيل دخول العضو الذي تم ترقيته
    page.fill("#email", member_email)
    page.fill("#password", member_password)
    page.click("button[type='submit']")
    page.wait_for_url("**/profile/", timeout=5000)

    # الذهاب لصفحة الإعدادات والتحقق من الترقية وتفعيل الصلاحيات
    page.goto(live_server.url + "/workspaces/acme-corp/settings/")
    page.wait_for_selector("#invite-email", timeout=5000)

    assert page.locator("span:has-text(': ADMIN')").is_visible()
    # كـ مشرف (Admin) يظهر خيار إرسال الدعوات
    assert page.locator("#invite-email").is_visible()
