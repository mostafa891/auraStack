import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.teams.models import Workspace, WorkspaceInvitation, WorkspaceMember

User = get_user_model()


@pytest.fixture
def workspace_setup(db):
    user_a = User.objects.create_user(email="tenant_a@example.com", password="Password123!")
    user_b = User.objects.create_user(email="tenant_b@example.com", password="Password123!")

    workspace_a = Workspace.objects.create(name="Workspace A", created_by=user_a)
    WorkspaceMember.objects.create(
        workspace=workspace_a, user=user_a, role=WorkspaceMember.RoleChoices.OWNER
    )

    workspace_b = Workspace.objects.create(name="Workspace B", created_by=user_b)
    WorkspaceMember.objects.create(
        workspace=workspace_b, user=user_b, role=WorkspaceMember.RoleChoices.OWNER
    )

    return {
        "user_a": user_a,
        "user_b": user_b,
        "workspace_a": workspace_a,
        "workspace_b": workspace_b,
    }


@pytest.mark.django_db
def test_workspace_settings_isolation(client, workspace_setup):
    """Verifies that a user cannot access workspace settings for a workspace they do not belong to."""
    client.force_login(workspace_setup["user_a"])

    # Attempt to access Workspace B settings
    response = client.get(
        reverse("teams:workspace_settings", kwargs={"slug": workspace_setup["workspace_b"].slug})
    )

    # Should redirect with unauthorized status
    assert response.status_code == 302


@pytest.mark.django_db
def test_workspace_update_settings_isolation(client, workspace_setup):
    """Verifies that a user cannot update settings for a workspace they do not belong to."""
    client.force_login(workspace_setup["user_a"])

    # Attempt POST to update Workspace B name
    response = client.post(
        reverse("teams:workspace_settings", kwargs={"slug": workspace_setup["workspace_b"].slug}),
        data={"name": "Hacked Name"},
    )
    assert response.status_code == 302

    # Verify update was blocked and name remains unchanged
    workspace_setup["workspace_b"].refresh_from_db()
    assert workspace_setup["workspace_b"].name == "Workspace B"


@pytest.mark.django_db
def test_workspace_invitation_isolation(client, workspace_setup):
    """Verifies that a user cannot send member invitations for a workspace they do not belong to."""
    client.force_login(workspace_setup["user_a"])

    # Attempt POST to invite member to Workspace B
    response = client.post(
        reverse("teams:workspace_invite", kwargs={"slug": workspace_setup["workspace_b"].slug}),
        data={"email": "new_member@example.com", "role": "MEMBER"},
    )
    assert response.status_code == 302

    # Verify invitation was blocked
    assert WorkspaceInvitation.objects.filter(workspace=workspace_setup["workspace_b"]).count() == 0
