import pytest
from playwright.sync_api import Page


@pytest.mark.django_db(transaction=True)
def test_teams_and_workspaces_e2e_flow(live_server, page: Page):
    """End-to-end testing of workspace lifecycle: creation, settings, and invitation flows."""

    # 1. Navigate to registration and register E2E user
    page.on("console", lambda msg: print(f"[Browser Console] {msg.text}"))
    page.on("pageerror", lambda err: print(f"[Browser PageError] {err}"))

    page.goto(live_server.url + "/auth/register/")
    page.wait_for_selector("#email", timeout=5000)

    page.fill("#email", "teams_e2e_user@aurastack.com")
    page.fill("#password", "Password123!")
    page.fill("#password_confirm", "Password123!")
    page.click("button[type='submit']")

    # 2. Wait for redirect to profile
    page.wait_for_url("**/profile/", timeout=5000)
    assert page.locator("h2:has-text('User Preferences & Settings')").is_visible()

    # 3. Click "Manage Workspaces"
    page.click("a:has-text('Manage Workspaces')")

    # 4. Wait for redirect to workspaces list
    page.wait_for_url("**/workspaces/", timeout=5000)
    assert page.locator("h1:has-text('Workspaces')").is_visible()
    assert page.locator("h3:has-text('No Workspaces Found')").is_visible()

    # 5. Open Create Workspace modal
    page.click("button:has-text('Create Workspace')")
    page.wait_for_selector("#modal-name", timeout=2000)

    # 6. Fill workspace name and submit
    page.fill("#modal-name", "Acme Team E2E")
    page.click("button[type='submit']:has-text('Create Workspace')")

    # 7. Verify auto-redirect to created workspace settings
    page.wait_for_url("**/workspaces/acme-team-e2e/settings/", timeout=5000)
    assert page.locator("h1:has-text('Acme Team E2E Settings')").is_visible()

    # 8. Verify owner member is in members table
    assert page.locator("td:has-text('teams_e2e_user@aurastack.com')").is_visible()

    # 9. Send invitation to new member
    page.fill("#invite-email", "invited_e2e@aurastack.com")
    page.select_option("#invite-role", "ADMIN")
    page.click("button:has-text('Send Invitation')")

    # 10. Verify pending invitation appears in list
    page.wait_for_selector("[title='invited_e2e@aurastack.com']", timeout=3000)
    assert page.locator("[title='invited_e2e@aurastack.com']").is_visible()
