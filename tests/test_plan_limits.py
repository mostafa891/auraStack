"""
Tests for plan limits enforcement.
Verifies that the invitation system rejects adding members once plan limit is reached.
"""

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.payments.models import ProviderChoices, Subscription, SubscriptionStatusChoices
from apps.payments.selectors import get_plan_limit, get_workspace_plan
from apps.teams.models import Workspace, WorkspaceMember
from apps.teams.services import WorkspaceService

User = get_user_model()


@pytest.fixture
def owner(db):
    return User.objects.create_user(email="plan_owner@test.com", password="Password123!")


@pytest.fixture
def workspace_with_owner(db, owner):
    workspace = Workspace.objects.create(name="Plan Test Workspace", created_by=owner)
    WorkspaceMember.objects.create(
        workspace=workspace, user=owner, role=WorkspaceMember.RoleChoices.OWNER
    )
    return workspace


# ============================================================
# Selectors Tests
# ============================================================


@pytest.mark.django_db
def test_get_workspace_plan_returns_free_by_default(workspace_with_owner):
    """Workspace without subscription defaults to free plan."""
    plan = get_workspace_plan(workspace_with_owner)
    assert plan == "free"


@pytest.mark.django_db
def test_get_workspace_plan_returns_active_plan(workspace_with_owner):
    """Workspace with active subscription returns correct plan."""
    Subscription.objects.create(
        workspace=workspace_with_owner,
        provider=ProviderChoices.STRIPE,
        subscription_id="sub_test123",
        plan_id="pro",
        status=SubscriptionStatusChoices.ACTIVE,
        current_period_end=timezone.now() + timezone.timedelta(days=30),
    )
    plan = get_workspace_plan(workspace_with_owner)
    assert plan == "pro"


@pytest.mark.django_db
def test_get_workspace_plan_ignores_inactive_subscription(workspace_with_owner):
    """Expired subscription falls back to free plan."""
    Subscription.objects.create(
        workspace=workspace_with_owner,
        provider=ProviderChoices.STRIPE,
        subscription_id="sub_canceled",
        plan_id="pro",
        status=SubscriptionStatusChoices.CANCELED,
        current_period_end=timezone.now() - timezone.timedelta(days=1),
    )
    plan = get_workspace_plan(workspace_with_owner)
    assert plan == "free"


@pytest.mark.django_db
def test_get_plan_limit_free(workspace_with_owner):
    """Free plan: max_members = 3."""
    limit = get_plan_limit(workspace_with_owner, "max_members")
    assert limit == 3


@pytest.mark.django_db
def test_get_plan_limit_pro(workspace_with_owner):
    """Pro plan: max_members = 20."""
    Subscription.objects.create(
        workspace=workspace_with_owner,
        provider=ProviderChoices.STRIPE,
        subscription_id="sub_pro",
        plan_id="pro",
        status=SubscriptionStatusChoices.ACTIVE,
        current_period_end=timezone.now() + timezone.timedelta(days=30),
    )
    limit = get_plan_limit(workspace_with_owner, "max_members")
    assert limit == 20


# ============================================================
# invite_member limits enforcement tests
# ============================================================


@pytest.mark.django_db
def test_invite_blocked_when_free_plan_full(db, workspace_with_owner, owner):
    """
    Free plan: 3 members limit — invitation rejected when limit reached.
    Owner counts as 1 member, adding 2 more members = 3 total.
    """
    for i in range(2):
        user = User.objects.create_user(email=f"member{i}@test.com", password="Password123!")
        WorkspaceMember.objects.create(
            workspace=workspace_with_owner, user=user, role=WorkspaceMember.RoleChoices.MEMBER
        )

    # Membership = 3 (Free plan maximum)
    assert workspace_with_owner.members.count() == 3

    result = WorkspaceService.invite_member(
        workspace=workspace_with_owner,
        invited_by=owner,
        email="newmember@test.com",
        role="MEMBER",
    )
    assert not result.success
    assert "maximum" in result.message.lower()


@pytest.mark.django_db
def test_invite_allowed_when_below_limit(db, workspace_with_owner, owner):
    """Free plan: below 3 members — invitation accepted."""
    # Owner only = 1 member (below limit)
    result = WorkspaceService.invite_member(
        workspace=workspace_with_owner,
        invited_by=owner,
        email="invited@test.com",
        role="MEMBER",
    )
    assert result.success


@pytest.mark.django_db
def test_invite_allowed_when_pro_plan_not_full(db, workspace_with_owner, owner):
    """Pro plan: limit 20 — invitation accepted with 3 members."""
    Subscription.objects.create(
        workspace=workspace_with_owner,
        provider=ProviderChoices.STRIPE,
        subscription_id="sub_pro_test",
        plan_id="pro",
        status=SubscriptionStatusChoices.ACTIVE,
        current_period_end=timezone.now() + timezone.timedelta(days=30),
    )
    for i in range(2):
        user = User.objects.create_user(email=f"pro_member{i}@test.com", password="Password123!")
        WorkspaceMember.objects.create(
            workspace=workspace_with_owner, user=user, role=WorkspaceMember.RoleChoices.MEMBER
        )

    result = WorkspaceService.invite_member(
        workspace=workspace_with_owner,
        invited_by=owner,
        email="new_pro_member@test.com",
        role="MEMBER",
    )
    assert result.success
