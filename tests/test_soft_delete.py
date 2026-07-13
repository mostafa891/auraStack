import pytest
from django.urls import reverse

from apps.teams.models import Workspace, WorkspaceMember
from apps.teams.services import WorkspaceService
from apps.users.models import CustomUser


@pytest.fixture
def soft_delete_setup():
    """تهيئة مستخدم ومساحة عمل للاختبار."""
    user = CustomUser.objects.create_user(email="owner@example.com", password="Password123!")
    result = WorkspaceService.create_workspace(name="Test Workspace", user=user)
    workspace = result.data
    return {
        "user": user,
        "workspace": workspace,
    }


@pytest.mark.django_db
def test_workspace_soft_delete_mechanics(soft_delete_setup):
    """التحقق من أن حذف مساحة العمل يغير قيم deleted_at ويخفيها من الاستعلامات الافتراضية."""
    user = soft_delete_setup["user"]
    workspace = soft_delete_setup["workspace"]

    # التحقق من أن مساحة العمل والمسؤول نشطون حالياً
    assert Workspace.objects.filter(id=workspace.id).exists()
    assert WorkspaceMember.objects.filter(workspace=workspace, user=user).exists()

    # تنفيذ الحذف الناعم عبر الخدمة
    result = WorkspaceService.delete_workspace(workspace=workspace, operator=user)
    assert result.success is True

    # 1. التحقق من الاختفاء من الاستعلامات القياسية
    assert not Workspace.objects.filter(id=workspace.id).exists()
    assert not WorkspaceMember.objects.filter(workspace=workspace, user=user).exists()

    # 2. التحقق من الوجود عند جلب الكل (all_objects) مع امتلاك قيمة deleted_at
    archived_workspace = Workspace.all_objects.get(id=workspace.id)
    assert archived_workspace.deleted_at is not None

    archived_member = WorkspaceMember.all_objects.get(workspace=workspace, user=user)
    assert archived_member.deleted_at is not None


@pytest.mark.django_db
def test_workspace_restoration(soft_delete_setup):
    """التحقق من إمكانية استعادة مساحة العمل وعضوياتها المحذوفة ناعماً."""
    user = soft_delete_setup["user"]
    workspace = soft_delete_setup["workspace"]

    # الحذف
    WorkspaceService.delete_workspace(workspace=workspace, operator=user)

    # الاستعادة
    result = WorkspaceService.restore_workspace(workspace_id=str(workspace.id), operator=user)
    assert result.success is True

    # التحقق من استعادة النشاط بالكامل
    assert Workspace.objects.filter(id=workspace.id).exists()
    assert WorkspaceMember.objects.filter(workspace=workspace, user=user).exists()

    refreshed_workspace = Workspace.objects.get(id=workspace.id)
    assert refreshed_workspace.deleted_at is None


@pytest.mark.django_db
def test_deleted_workspace_views_not_found(client, soft_delete_setup):
    """التحقق من أن مساحات العمل المحذوفة ناعماً ترجع 404 عند محاولة فتح إعداداتها."""
    user = soft_delete_setup["user"]
    workspace = soft_delete_setup["workspace"]

    client.force_login(user)

    # الحذف
    WorkspaceService.delete_workspace(workspace=workspace, operator=user)

    # فتح الإعدادات يجب أن يرجع 404
    response = client.get(reverse("teams:workspace_settings", kwargs={"slug": workspace.slug}))
    assert response.status_code == 404
