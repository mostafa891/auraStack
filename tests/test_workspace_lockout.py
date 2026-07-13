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

    # إضافة أعضاء إضافيين لمحاكاة تجاوز الحد
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
    """التحقق من أن مساحة العمل يتم قفلها (is_locked=True)

    عند تجاوز حد الأعضاء للباقة المجانية (Free: max 3 members).
    """
    # حالياً في قاعدة البيانات لدينا 4 أعضاء (المالك + 3 أعضاء)
    # والاشتراك الافتراضي هو Free

    client.force_login(lockout_setup["owner"])

    # تعيين مساحة العمل كنشطة في الجلسة
    session = client.session
    session["active_workspace_id"] = str(lockout_setup["workspace"].id)
    session.save()

    response = client.get(reverse("profile"))

    # التحقق من أن خصائص Inertia المشتركة تحتوي على قفل لمساحة العمل
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
    """التحقق من قفل الحساب عند إلغاء أو عدم سداد اشتراك باقة Pro."""
    client.force_login(lockout_setup["owner"])

    # تعيين مساحة العمل كنشطة
    session = client.session
    session["active_workspace_id"] = str(lockout_setup["workspace"].id)
    session.save()

    # إنشاء اشتراك Pro غير نشط (ملغى أو متأخر السداد)
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
