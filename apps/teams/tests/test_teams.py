import pytest
from django.test import Client
from django.urls import reverse

from apps.teams.models import Workspace, WorkspaceInvitation, WorkspaceMember
from apps.teams.services import WorkspaceService
from apps.users.models import CustomUser


@pytest.mark.django_db
def test_workspace_slug_autogeneration():
    """التحقق من التوليد التلقائي للـ slug عند الإنشاء ودعم اللغة العربية."""
    user = CustomUser.objects.create_user(email="owner@auraflow.com", password="Password123!")

    # 1. اختبار اسم إنجليزي عادي
    ws1 = Workspace.objects.create(name="Acme Corp", created_by=user)
    assert ws1.slug == "acme-corp"

    # 2. اختبار اسم عربي
    ws2 = Workspace.objects.create(name="مساحة عملي الخاصة", created_by=user)
    assert ws2.slug == "مساحة-عملي-الخاصة"

    # 3. اختبار الأسماء المكررة لضمان الفرادة تلقائياً
    ws3 = Workspace.objects.create(name="Acme Corp", created_by=user)
    assert ws3.slug == "acme-corp-1"

    ws4 = Workspace.objects.create(name="Acme Corp", created_by=user)
    assert ws4.slug == "acme-corp-2"

    # 4. اختبار رموز خاصة فقط (توليد slug عشوائي كبديل للرموز)
    ws5 = Workspace.objects.create(name="!!! @@@", created_by=user)
    assert ws5.slug.startswith("workspace-")
    assert len(ws5.slug) == 16  # workspace- + 6 hex chars


@pytest.mark.django_db
def test_workspace_service_create_workspace():
    """التحقق من إنشاء مساحة عمل وإضافة المالك كعضو عبر الخدمة."""
    user = CustomUser.objects.create_user(email="owner@auraflow.com", password="Password123!")
    result = WorkspaceService.create_workspace(name="My Workspace", user=user)

    assert result.success is True
    workspace = result.data
    assert workspace.name == "My Workspace"
    assert workspace.slug == "my-workspace"

    # التحقق من العضوية التلقائية كمالك
    member = WorkspaceMember.objects.filter(workspace=workspace, user=user).first()
    assert member is not None
    assert member.role == WorkspaceMember.RoleChoices.OWNER


@pytest.mark.django_db
def test_workspace_service_invite_member():
    """التحقق من دعوة الأعضاء للفريق والقيود المفروضة عليها."""
    owner_user = CustomUser.objects.create_user(email="owner@auraflow.com", password="Password123!")
    member_user = CustomUser.objects.create_user(
        email="member@auraflow.com", password="Password123!"
    )

    ws = WorkspaceService.create_workspace(name="Acme", user=owner_user).data

    # 1. المالك يدعو عضو جديد
    result = WorkspaceService.invite_member(
        workspace=ws, invited_by=owner_user, email="new@auraflow.com", role="ADMIN"
    )
    assert result.success is True
    invitation = result.data
    assert invitation.email == "new@auraflow.com"
    assert invitation.role == WorkspaceMember.RoleChoices.ADMIN
    assert invitation.status == WorkspaceInvitation.StatusChoices.PENDING

    # 2. المالك يحاول دعوة عضو مسجل بالفعل في الفريق
    WorkspaceMember.objects.create(
        workspace=ws, user=member_user, role=WorkspaceMember.RoleChoices.MEMBER
    )
    result = WorkspaceService.invite_member(
        workspace=ws, invited_by=owner_user, email="member@auraflow.com", role="MEMBER"
    )
    assert result.success is False
    assert "already a member" in result.message

    # 3. المالك يحاول إرسال دعوة معلقة ومكررة لنفس البريد قبل انتهاء صلاحيتها
    result = WorkspaceService.invite_member(
        workspace=ws, invited_by=owner_user, email="new@auraflow.com", role="MEMBER"
    )
    assert result.success is False
    assert "active invitation" in result.message


@pytest.mark.django_db
def test_workspace_service_accept_invitation():
    """التحقق من قبول الدعوات بنجاح والقيود الأمنية للمدعوين."""
    owner_user = CustomUser.objects.create_user(email="owner@auraflow.com", password="Password123!")
    invited_user = CustomUser.objects.create_user(
        email="invited@auraflow.com", password="Password123!"
    )
    other_user = CustomUser.objects.create_user(email="other@auraflow.com", password="Password123!")

    ws = WorkspaceService.create_workspace(name="Acme", user=owner_user).data
    invitation = WorkspaceService.invite_member(
        workspace=ws, invited_by=owner_user, email="invited@auraflow.com", role="ADMIN"
    ).data

    # 1. محاولة القبول ببريد إلكتروني غير مطابق للدعوة
    result = WorkspaceService.accept_invitation(token_uuid=invitation.token, user=other_user)
    assert result.success is False
    assert "logged in as" in result.message

    # 2. القبول الصحيح
    result = WorkspaceService.accept_invitation(token_uuid=invitation.token, user=invited_user)
    assert result.success is True
    member = result.data
    assert member.role == WorkspaceMember.RoleChoices.ADMIN

    # التحقق من تحديث حالة الدعوة
    invitation.refresh_from_db()
    assert invitation.status == WorkspaceInvitation.StatusChoices.ACCEPTED


@pytest.mark.django_db
def test_workspace_service_remove_member_and_leave():
    """التحقق من إزالة الأعضاء ومغادرة مساحات العمل وقيود المالك الوحيد."""
    owner_user = CustomUser.objects.create_user(email="owner@auraflow.com", password="Password123!")
    admin_user = CustomUser.objects.create_user(email="admin@auraflow.com", password="Password123!")
    member_user = CustomUser.objects.create_user(
        email="member@auraflow.com", password="Password123!"
    )

    ws = WorkspaceService.create_workspace(name="Acme", user=owner_user).data

    # إضافة الأعضاء
    mem_admin = WorkspaceMember.objects.create(
        workspace=ws, user=admin_user, role=WorkspaceMember.RoleChoices.ADMIN
    )
    mem_member = WorkspaceMember.objects.create(
        workspace=ws, user=member_user, role=WorkspaceMember.RoleChoices.MEMBER
    )

    # 1. عضو عادي يحاول إزالة مشرف (ADMIN) -> فشل
    result = WorkspaceService.remove_member(
        workspace=ws, member_id=str(mem_admin.id), operator=member_user
    )
    assert result.success is False
    assert "Access denied" in result.message

    # 2. مشرف (ADMIN) يحاول إزالة عضو عادي -> نجاح
    result = WorkspaceService.remove_member(
        workspace=ws, member_id=str(mem_member.id), operator=admin_user
    )
    assert result.success is True
    assert WorkspaceMember.objects.filter(id=mem_member.id).exists() is False

    # 3. المالك الوحيد يحاول مغادرة مساحة العمل -> فشل لمنع المساحات بلا مالك
    mem_owner = WorkspaceMember.objects.filter(workspace=ws, user=owner_user).first()
    result = WorkspaceService.remove_member(
        workspace=ws, member_id=str(mem_owner.id), operator=owner_user
    )
    assert result.success is False
    assert "only Owner" in result.message


@pytest.mark.django_db
def test_workspace_views_flow():
    """اختبار مسار الطلبات والتوجيه لصفحات إدارة مساحات العمل."""
    client = Client()
    user = CustomUser.objects.create_user(email="user@auraflow.com", password="Password123!")
    client.force_login(user)

    # 1. اختبار استعراض قائمة مساحات العمل
    response = client.get(reverse("teams:workspace_list"))
    assert response.status_code == 200

    # 2. اختبار إنشاء مساحة عمل جديدة عبر POST
    response = client.post(reverse("teams:workspace_list"), {"name": "New Team"})
    assert response.status_code == 302  # توجيه لصفحة الإعدادات

    ws = Workspace.objects.get(name="New Team")
    assert response.url == reverse("teams:workspace_settings", kwargs={"slug": ws.slug})

    # 3. اختبار عرض صفحة الإعدادات لمساحة العمل الجديدة
    response = client.get(reverse("teams:workspace_settings", kwargs={"slug": ws.slug}))
    assert response.status_code == 200
