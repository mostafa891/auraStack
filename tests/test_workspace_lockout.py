import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.payments.models import Subscription, SubscriptionStatusChoices
from apps.teams.models import Workspace, WorkspaceMember

User = get_user_model()


@pytest.fixture
def lockout_setup(db):
    owner = User.objects.create_user(email="owner@example.com", password="Password123!")
    workspace = Workspace.objects.create(name="Limits Test Workspace", created_by=owner)
    WorkspaceMember.objects.create(
        workspace=workspace, user=owner, role=WorkspaceMember.RoleChoices.OWNER
    )

    # Add extra members to simulate exceeding plan limit
    user_a = User.objects.create_user(email="member_a@example.com", password="Password123!")
    user_b = User.objects.create_user(email="member_b@example.com", password="Password123!")
    user_c = User.objects.create_user(email="member_c@example.com", password="Password123!")

    WorkspaceMember.objects.create(
        workspace=workspace, user=user_a, role=WorkspaceMember.RoleChoices.MEMBER
    )
    WorkspaceMember.objects.create(
        workspace=workspace, user=user_b, role=WorkspaceMember.RoleChoices.MEMBER
    )
    WorkspaceMember.objects.create(
        workspace=workspace, user=user_c, role=WorkspaceMember.RoleChoices.MEMBER
    )

    return {
        "owner": owner,
        "workspace": workspace,
    }


@pytest.mark.django_db
def test_workspace_lockout_when_exceeding_free_limit(client, lockout_setup):
    """Verifies that workspace gets locked (is_locked=True) when member count exceeds Free plan limit (3 members)."""
    # Database currently has 4 members (Owner + 3 Members) with default Free plan
    client.force_login(lockout_setup["owner"])

    # Set active workspace in session
    session = client.session
    session["active_workspace_id"] = str(lockout_setup["workspace"].id)
    session.save()

    response = client.get(reverse("profile"))

    # Verify Inertia shared props include workspace lockout flag
    import json

    page = response.context["page"]
    if isinstance(page, str):
        page = json.loads(page)
    auth_prop = page["props"]["auth"]
    active_ws = auth_prop["active_workspace"]

    assert active_ws["subscription"]["is_locked"] is True
    assert active_ws["subscription"]["member_count"] == 4
    assert active_ws["subscription"]["max_members"] == 3


@pytest.mark.django_db
def test_workspace_lockout_when_subscription_canceled(client, lockout_setup):
    """Verifies workspace lockout when Pro subscription is canceled or unpaid."""
    client.force_login(lockout_setup["owner"])

    # Set active workspace in session
    session = client.session
    session["active_workspace_id"] = str(lockout_setup["workspace"].id)
    session.save()

    # Create inactive Pro subscription (canceled)
    Subscription.objects.create(
        workspace=lockout_setup["workspace"],
        plan_id="pro",
        status=SubscriptionStatusChoices.CANCELED,
        provider="STRIPE",
    )

    response = client.get(reverse("profile"))

    import json

    page = response.context["page"]
    if isinstance(page, str):
        page = json.loads(page)
    auth_prop = page["props"]["auth"]
    active_ws = auth_prop["active_workspace"]

    assert active_ws["subscription"]["is_locked"] is True
