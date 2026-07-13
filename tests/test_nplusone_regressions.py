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

    # إنشاء 5 أعضاء إضافيين
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
    """
    التحقق من عدم وجود استعلامات N+1 عند تحميل صفحة إعدادات مساحة العمل وقائمة الأعضاء.
    يجب جلب قائمة الأعضاء وبيانات حساباتهم باستعلامات مدمجة وموحدة (select_related).
    """
    client.force_login(workspace_with_multiple_members["owner"])

    # طلب تمهيدي (Warm-up) لتهيئة التخزين المؤقت وتجنب تباين أعداد الاستعلامات الأولية
    client.get(
        reverse(
            "teams:workspace_settings",
            kwargs={"slug": workspace_with_multiple_members["workspace"].slug},
        )
    )

    # 1. قياس عدد الاستعلامات لـ 6 أعضاء (المالك + 5 أعضاء)
    with CaptureQueriesContext(connection) as ctx_six_members:
        response = client.get(
            reverse(
                "teams:workspace_settings",
                kwargs={"slug": workspace_with_multiple_members["workspace"].slug},
            )
        )
        assert response.status_code == 200

    queries_with_six = len(ctx_six_members.captured_queries)

    # 2. إضافة 5 أعضاء آخرين (المجموع 11 عضواً)
    workspace = workspace_with_multiple_members["workspace"]
    for i in range(5, 10):
        member_user = User.objects.create_user(
            email=f"member_{i}@example.com", password="Password123!"
        )
        WorkspaceMember.objects.create(
            workspace=workspace, user=member_user, role=WorkspaceMember.RoleChoices.MEMBER
        )

    # 3. قياس عدد الاستعلامات لـ 11 عضواً
    with CaptureQueriesContext(connection) as ctx_eleven_members:
        response = client.get(reverse("teams:workspace_settings", kwargs={"slug": workspace.slug}))
        assert response.status_code == 200

    queries_with_eleven = len(ctx_eleven_members.captured_queries)

    # التحقق من أن زيادة عدد الأعضاء لا تزيد عدد الاستعلامات (حماية ضد N+1)
    assert queries_with_eleven <= queries_with_six, (
        f"N+1 Query Detected! Queries increased from {queries_with_six} to {queries_with_eleven} "
        f"when adding 5 more members."
    )
