import pytest
from django.contrib.auth import get_user_model
from playwright.sync_api import Page

from apps.teams.models import WorkspaceInvitation


@pytest.mark.django_db(transaction=True)
def test_workspace_permissions_and_invite_acceptance_e2e(live_server, page: Page):
    """End-to-end verification of workspace role permissions (Owner, Admin, Member) and invitation flows."""
    User = get_user_model()

    # 1. Create owner account and setup workspace
    owner_email = "owner_perm@aurastack.com"
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

    # Wait for redirect to created workspace settings
    page.wait_for_url("**/workspaces/acme-corp/settings/", timeout=5000)
    assert page.locator("h1", has_text="Acme Corp").is_visible()

    # 2. Invite new member with MEMBER role
    member_email = "member_perm@aurastack.com"
    page.fill("#invite-email", member_email)
    page.select_option("#invite-role", "MEMBER")
    page.click("button:has-text('Send Invitation')")

    # Wait for pending invitation to appear
    page.wait_for_selector(f"[title='{member_email}']", timeout=5000)

    # 3. Extract invitation token and accept invitation as new member
    invitation = WorkspaceInvitation.objects.get(email=member_email)
    invite_token = str(invitation.token)

    # Logout owner
    page.goto(live_server.url + "/profile/")
    page.click("button:has-text('Logout')")
    page.wait_for_url("**/auth/login/", timeout=5000)

    # Register member user account
    member_password = "Password123!"
    User.objects.create_user(email=member_email, password=member_password)

    # Login member user
    page.fill("#email", member_email)
    page.fill("#password", member_password)
    page.click("button[type='submit']")
    page.wait_for_url("**/profile/", timeout=5000)

    # Visit direct invitation acceptance URL
    page.goto(live_server.url + f"/workspaces/invitations/{invite_token}/accept/")

    # Verify invitation acceptance and auto-redirect to settings
    page.wait_for_url("**/workspaces/acme-corp/settings/", timeout=5000)
    assert page.locator("h1", has_text="Acme Corp").is_visible()
    assert page.locator("span:has-text(': MEMBER')").is_visible()

    # 4. Verify MEMBER role restrictions (inputs disabled)
    name_input = page.locator("#name")
    assert name_input.is_disabled()
    slug_input = page.locator("#slug")
    assert slug_input.is_disabled()

    # Verify invitation form is hidden for non-admins
    assert not page.locator("#invite-email").is_visible()

    # 5. Promote member to ADMIN role by owner
    # Logout member
    page.goto(live_server.url + "/profile/")
    page.click("button:has-text('Logout')")
    page.wait_for_url("**/auth/login/", timeout=5000)

    # Login owner
    page.fill("#email", owner_email)
    page.fill("#password", owner_password)
    page.click("button[type='submit']")
    page.wait_for_url("**/profile/", timeout=5000)

    # Go to settings and promote member
    page.goto(live_server.url + "/workspaces/acme-corp/settings/")
    page.wait_for_selector("select", timeout=5000)

    # Select ADMIN role for member in members table
    page.locator(f"tr:has-text('{member_email}') select").select_option("ADMIN")
    page.wait_for_timeout(1000)

    # Logout owner
    page.goto(live_server.url + "/profile/")
    page.click("button:has-text('Logout')")
    page.wait_for_url("**/auth/login/", timeout=5000)

    # Login promoted member
    page.fill("#email", member_email)
    page.fill("#password", member_password)
    page.click("button[type='submit']")
    page.wait_for_url("**/profile/", timeout=5000)

    # Visit settings and verify ADMIN role & permissions enabled
    page.goto(live_server.url + "/workspaces/acme-corp/settings/")
    page.wait_for_selector("#invite-email", timeout=5000)

    assert page.locator("span:has-text(': ADMIN')").is_visible()
    assert page.locator("#invite-email").is_visible()
