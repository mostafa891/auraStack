import pytest
from django.urls import reverse

from apps.teams.models import Workspace, WorkspaceMember
from apps.teams.services import WorkspaceService
from apps.users.models import CustomUser


@pytest.fixture
def soft_delete_setup():
    """Initializes user and workspace for soft-delete tests."""
    user = CustomUser.objects.create_user(email="owner@example.com", password="Password123!")
    result = WorkspaceService.create_workspace(name="Test Workspace", user=user)
    workspace = result.data
    return {
        "user": user,
        "workspace": workspace,
    }


@pytest.mark.django_db
def test_workspace_soft_delete_mechanics(soft_delete_setup):
    """Verifies soft delete mechanic updates deleted_at timestamp and hides record from default queryset."""
    user = soft_delete_setup["user"]
    workspace = soft_delete_setup["workspace"]

    # Verify workspace and member are active initially
    assert Workspace.objects.filter(id=workspace.id).exists()
    assert WorkspaceMember.objects.filter(workspace=workspace, user=user).exists()

    # Execute soft delete via service layer
    result = WorkspaceService.delete_workspace(workspace=workspace, operator=user)
    assert result.success is True

    # 1. Verify hidden from standard manager querysets
    assert not Workspace.objects.filter(id=workspace.id).exists()
    assert not WorkspaceMember.objects.filter(workspace=workspace, user=user).exists()

    # 2. Verify present when querying all_objects manager with non-null deleted_at timestamp
    archived_workspace = Workspace.all_objects.get(id=workspace.id)
    assert archived_workspace.deleted_at is not None

    archived_member = WorkspaceMember.all_objects.get(workspace=workspace, user=user)
    assert archived_member.deleted_at is not None


@pytest.mark.django_db
def test_workspace_restoration(soft_delete_setup):
    """Verifies restoration of soft-deleted workspaces and associated memberships."""
    user = soft_delete_setup["user"]
    workspace = soft_delete_setup["workspace"]

    # Soft delete
    WorkspaceService.delete_workspace(workspace=workspace, operator=user)

    # Restore
    result = WorkspaceService.restore_workspace(workspace_id=str(workspace.id), operator=user)
    assert result.success is True

    # Verify active state restored
    assert Workspace.objects.filter(id=workspace.id).exists()
    assert WorkspaceMember.objects.filter(workspace=workspace, user=user).exists()

    refreshed_workspace = Workspace.objects.get(id=workspace.id)
    assert refreshed_workspace.deleted_at is None


@pytest.mark.django_db
def test_deleted_workspace_views_not_found(client, soft_delete_setup):
    """Verifies that accessing settings for soft-deleted workspace returns 404 Not Found."""
    user = soft_delete_setup["user"]
    workspace = soft_delete_setup["workspace"]

    client.force_login(user)

    # Soft delete
    WorkspaceService.delete_workspace(workspace=workspace, operator=user)

    # Accessing settings should return 404 Not Found
    response = client.get(reverse("teams:workspace_settings", kwargs={"slug": workspace.slug}))
    assert response.status_code == 404
