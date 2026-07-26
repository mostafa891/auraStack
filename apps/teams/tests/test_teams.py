import pytest
from django.test import Client
from django.urls import reverse

from apps.teams.models import Workspace, WorkspaceInvitation, WorkspaceMember
from apps.teams.services import WorkspaceService
from apps.users.models import CustomUser


@pytest.mark.django_db
def test_workspace_slug_autogeneration():
    """Verifies automatic slug generation upon workspace creation and unicode support."""
    user = CustomUser.objects.create_user(email="owner@aurastack.com", password="Password123!")

    # 1. Test standard English name
    ws1 = Workspace.objects.create(name="Acme Corp", created_by=user)
    assert ws1.slug == "acme-corp"

    # 2. Test Arabic / unicode name
    ws2 = Workspace.objects.create(name="مساحة عملي الخاصة", created_by=user)
    assert ws2.slug == "مساحة-عملي-الخاصة"

    # 3. Test duplicate names to ensure uniqueness counter
    ws3 = Workspace.objects.create(name="Acme Corp", created_by=user)
    assert ws3.slug == "acme-corp-1"

    ws4 = Workspace.objects.create(name="Acme Corp", created_by=user)
    assert ws4.slug == "acme-corp-2"

    # 4. Test special characters fallback slug generation
    ws5 = Workspace.objects.create(name="!!! @@@", created_by=user)
    assert ws5.slug.startswith("workspace-")
    assert len(ws5.slug) == 16  # workspace- + 6 hex chars


@pytest.mark.django_db
def test_workspace_service_create_workspace():
    """Verifies creating workspace and adding owner as member via service layer."""
    user = CustomUser.objects.create_user(email="owner@aurastack.com", password="Password123!")
    result = WorkspaceService.create_workspace(name="My Workspace", user=user)

    assert result.success is True
    workspace = result.data
    assert workspace.name == "My Workspace"
    assert workspace.slug == "my-workspace"

    # Verify owner member creation
    member = WorkspaceMember.objects.filter(workspace=workspace, user=user).first()
    assert member is not None
    assert member.role == WorkspaceMember.RoleChoices.OWNER


@pytest.mark.django_db
def test_workspace_service_invite_member():
    """Verifies inviting team members and enforcing validation constraints."""
    owner_user = CustomUser.objects.create_user(
        email="owner@aurastack.com", password="Password123!"
    )
    member_user = CustomUser.objects.create_user(
        email="member@aurastack.com", password="Password123!"
    )

    ws = WorkspaceService.create_workspace(name="Acme", user=owner_user).data

    # 1. Owner invites new member
    result = WorkspaceService.invite_member(
        workspace=ws, invited_by=owner_user, email="new@aurastack.com", role="ADMIN"
    )
    assert result.success is True
    invitation = result.data
    assert invitation.email == "new@aurastack.com"
    assert invitation.role == WorkspaceMember.RoleChoices.ADMIN
    assert invitation.status == WorkspaceInvitation.StatusChoices.PENDING

    # 2. Owner attempts to invite an existing team member
    WorkspaceMember.objects.create(
        workspace=ws, user=member_user, role=WorkspaceMember.RoleChoices.MEMBER
    )
    result = WorkspaceService.invite_member(
        workspace=ws, invited_by=owner_user, email="member@aurastack.com", role="MEMBER"
    )
    assert result.success is False
    assert "already a member" in result.message

    # 3. Owner attempts sending duplicate pending invitation before expiry
    result = WorkspaceService.invite_member(
        workspace=ws, invited_by=owner_user, email="new@aurastack.com", role="MEMBER"
    )
    assert result.success is False
    assert "active invitation" in result.message


@pytest.mark.django_db
def test_workspace_service_accept_invitation():
    """Verifies accepting invitations successfully and security restrictions."""
    owner_user = CustomUser.objects.create_user(
        email="owner@aurastack.com", password="Password123!"
    )
    invited_user = CustomUser.objects.create_user(
        email="invited@aurastack.com", password="Password123!"
    )
    other_user = CustomUser.objects.create_user(
        email="other@aurastack.com", password="Password123!"
    )

    ws = WorkspaceService.create_workspace(name="Acme", user=owner_user).data

    invitation = WorkspaceService.invite_member(
        workspace=ws, invited_by=owner_user, email="invited@aurastack.com", role="ADMIN"
    ).data

    # 1. Attempting acceptance with wrong user account
    result = WorkspaceService.accept_invitation(token_uuid=invitation.token, user=other_user)
    assert result.success is False
    assert "logged in as" in result.message

    # 2. Correct acceptance
    result = WorkspaceService.accept_invitation(token_uuid=invitation.token, user=invited_user)
    assert result.success is True
    member = result.data
    assert member.role == WorkspaceMember.RoleChoices.ADMIN

    # Verify invitation status updated
    invitation.refresh_from_db()
    assert invitation.status == WorkspaceInvitation.StatusChoices.ACCEPTED


@pytest.mark.django_db
def test_workspace_service_remove_member_and_leave():
    """Verifies member removal, workspace leaving, and sole owner safeguards."""
    owner_user = CustomUser.objects.create_user(
        email="owner@aurastack.com", password="Password123!"
    )
    admin_user = CustomUser.objects.create_user(
        email="admin@aurastack.com", password="Password123!"
    )
    member_user = CustomUser.objects.create_user(
        email="member@aurastack.com", password="Password123!"
    )

    ws = WorkspaceService.create_workspace(name="Acme", user=owner_user).data

    # Add members
    mem_admin = WorkspaceMember.objects.create(
        workspace=ws, user=admin_user, role=WorkspaceMember.RoleChoices.ADMIN
    )
    mem_member = WorkspaceMember.objects.create(
        workspace=ws, user=member_user, role=WorkspaceMember.RoleChoices.MEMBER
    )

    # 1. Regular member attempts to remove an ADMIN -> failure
    result = WorkspaceService.remove_member(
        workspace=ws, member_id=str(mem_admin.id), operator=member_user
    )
    assert result.success is False
    assert "Access denied" in result.message

    # 2. ADMIN attempts to remove a regular MEMBER -> success
    result = WorkspaceService.remove_member(
        workspace=ws, member_id=str(mem_member.id), operator=admin_user
    )
    assert result.success is True
    assert WorkspaceMember.objects.filter(id=mem_member.id).exists() is False

    # 3. Sole owner attempts to leave workspace -> failure to prevent unowned workspace
    mem_owner = WorkspaceMember.objects.filter(workspace=ws, user=owner_user).first()
    result = WorkspaceService.remove_member(
        workspace=ws, member_id=str(mem_owner.id), operator=owner_user
    )
    assert result.success is False
    assert "only Owner" in result.message


@pytest.mark.django_db
def test_workspace_views_flow():
    """Tests request flow and routing for workspace management views."""
    client = Client()
    user = CustomUser.objects.create_user(email="user@aurastack.com", password="Password123!")
    client.force_login(user)

    # 1. Test rendering workspace list
    response = client.get(reverse("teams:workspace_list"))
    assert response.status_code == 200

    # 2. Test creating new workspace via POST
    response = client.post(reverse("teams:workspace_list"), {"name": "New Team"})
    assert response.status_code == 302  # Redirects to workspace settings

    ws = Workspace.objects.get(name="New Team")
    assert response.url == reverse("teams:workspace_settings", kwargs={"slug": ws.slug})

    # 3. Test rendering workspace settings page
    response = client.get(reverse("teams:workspace_settings", kwargs={"slug": ws.slug}))
    assert response.status_code == 200
