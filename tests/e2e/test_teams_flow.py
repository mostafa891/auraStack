import pytest
from playwright.sync_api import Page


@pytest.mark.django_db(transaction=True)
def test_teams_and_workspaces_e2e_flow(live_server, page: Page):
    """اختبار E2E شامل لدورة حياة مساحة العمل: إنشاء، عرض الإعدادات، ودعوة أعضاء الفريق."""

    # 1. التوجه لصفحة التسجيل وإنشاء مستخدم E2E
    page.on("console", lambda msg: print(f"[Browser Console] {msg.text}"))
    page.on("pageerror", lambda err: print(f"[Browser PageError] {err}"))

    page.goto(live_server.url + "/auth/register/")
    page.wait_for_selector("#email", timeout=5000)

    page.fill("#email", "teams_e2e_user@auraflow.com")
    page.fill("#password", "Password123!")
    page.fill("#password_confirm", "Password123!")
    page.click("button[type='submit']")

    # 2. انتظار التحويل لصفحة الملف الشخصي
    page.wait_for_url("**/profile/", timeout=5000)
    assert page.locator("h2:has-text('User Preferences & Settings')").is_visible()

    # 3. الضغط على رابط "إدارة مساحات العمل"
    page.click("a:has-text('Manage Workspaces')")

    # 4. انتظار التحويل لصفحة مساحات العمل والتحقق من عدم وجود مساحات حالياً
    page.wait_for_url("**/workspaces/", timeout=5000)
    assert page.locator("h1:has-text('Workspaces')").is_visible()
    assert page.locator("h3:has-text('No Workspaces Found')").is_visible()

    # 5. الضغط على زر إنشاء مساحة عمل جديدة وفتح المودال
    page.click("button:has-text('Create Workspace')")
    page.wait_for_selector("#modal-name", timeout=2000)

    # 6. تعبئة اسم مساحة العمل وإرسالها
    page.fill("#modal-name", "Acme Team E2E")
    page.click("button[type='submit']:has-text('Create Workspace')")

    # 7. التحقق من التوجيه التلقائي لصفحة إعدادات مساحة العمل المنشأة حديثاً
    page.wait_for_url("**/workspaces/acme-team-e2e/settings/", timeout=5000)
    assert page.locator("h1:has-text('Acme Team E2E Settings')").is_visible()
    assert page.locator("span:has-text('Your Role: OWNER')").is_visible()

    # 8. التحقق من وجود جدول الأعضاء وبه منشئ مساحة العمل (المالك)
    assert page.locator("td:has-text('teams_e2e_user@auraflow.com')").is_visible()
    assert page.locator("span:has-text('Your Role: OWNER')").is_visible()

    # 9. تعبئة دعوة لعضو جديد وإرسالها
    page.fill("#invite-email", "invited_e2e@auraflow.com")
    page.select_option("#invite-role", "ADMIN")
    page.click("button:has-text('Send Invitation')")

    # 10. انتظار ظهور الدعوة المعلقة في قسم الدعوات
    page.wait_for_selector("[title='invited_e2e@auraflow.com']", timeout=3000)
    assert page.locator("[title='invited_e2e@auraflow.com']").is_visible()
    assert page.locator("text=Role: Admin").is_visible()
