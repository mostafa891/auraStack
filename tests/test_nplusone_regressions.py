import pytest
from django.contrib.auth import get_user_model
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from apps.teams.models import Workspace, WorkspaceMember

User = get_user_model()


@pytest.fixture
def workspace_with_multiple_members(db):
    owner = User.objects.create_user(email="owner@example.com", password="Password123!")
    workspace = Workspace.objects.create(name="N+1 Query Test Workspace", created_by=owner)
    WorkspaceMember.objects.create(
        workspace=workspace, user=owner, role=WorkspaceMember.RoleChoices.OWNER
    )

    # Create 5 extra members
    for i in range(5):
        member_user = User.objects.create_user(
            email=f"member_{i}@example.com", password="Password123!"
        )
        WorkspaceMember.objects.create(
            workspace=workspace, user=member_user, role=WorkspaceMember.RoleChoices.MEMBER
        )
    return {
        "owner": owner,
        "workspace": workspace,
    }


@pytest.mark.django_db
def test_workspace_settings_no_nplusone_queries(client, workspace_with_multiple_members):
    """Verifies no N+1 query regression on workspace settings page when scaling member counts.

    Ensures select_related / prefetch_related query optimizations are active.
    """
    client.force_login(workspace_with_multiple_members["owner"])

    # Warm-up request to populate session / cache context
    client.get(
        reverse(
            "teams:workspace_settings",
            kwargs={"slug": workspace_with_multiple_members["workspace"].slug},
        )
    )

    # 1. Capture query count for 6 members (Owner + 5 members)
    with CaptureQueriesContext(connection) as ctx_six_members:
        response = client.get(
            reverse(
                "teams:workspace_settings",
                kwargs={"slug": workspace_with_multiple_members["workspace"].slug},
            )
        )
        assert response.status_code == 200

    queries_with_six = len(ctx_six_members.captured_queries)

    # 2. Add 5 more members (total 11 members)
    workspace = workspace_with_multiple_members["workspace"]
    for i in range(5, 10):
        member_user = User.objects.create_user(
            email=f"member_{i}@example.com", password="Password123!"
        )
        WorkspaceMember.objects.create(
            workspace=workspace, user=member_user, role=WorkspaceMember.RoleChoices.MEMBER
        )

    # 3. Capture query count for 11 members
    with CaptureQueriesContext(connection) as ctx_eleven_members:
        response = client.get(reverse("teams:workspace_settings", kwargs={"slug": workspace.slug}))
        assert response.status_code == 200

    queries_with_eleven = len(ctx_eleven_members.captured_queries)

    # Verify query count remains constant regardless of member count (N+1 protection)
    assert queries_with_eleven <= queries_with_six, (
        f"N+1 Query Detected! Queries increased from {queries_with_six} to {queries_with_eleven} "
        f"when adding 5 more members."
    )
