from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from inertia import render, share

from apps.teams.models import Workspace, WorkspaceInvitation, WorkspaceMember
from apps.teams.selectors import (
    get_workspace_membership,
    list_deleted_user_workspaces,
    list_workspace_members,
    list_workspace_pending_invitations,
)
from apps.teams.services import WorkspaceService
from common.utils.request import get_request_data


class WorkspaceListView(LoginRequiredMixin, View):
    """صفحة استعراض مساحات العمل للمستخدم وإنشاء مساحة جديدة."""

    login_url = "auth:login"

    def get(self, request):
        deleted_workspaces = [
            {
                "id": str(w.id),
                "name": w.name,
                "slug": w.slug,
                "deleted_at": w.deleted_at.strftime("%Y-%m-%d"),
            }
            for w in list_deleted_user_workspaces(request.user)
        ]
        return render(
            request, "Teams/WorkspaceList", props={"deleted_workspaces": deleted_workspaces}
        )

    def post(self, request):
        data = get_request_data(request)
        name = data.get("name", "").strip()

        if not name:
            share(request, errors={"name": ["Workspace name is required"]})
            deleted_workspaces = [
                {
                    "id": str(w.id),
                    "name": w.name,
                    "slug": w.slug,
                    "deleted_at": w.deleted_at.strftime("%Y-%m-%d"),
                }
                for w in list_deleted_user_workspaces(request.user)
            ]
            return render(
                request, "Teams/WorkspaceList", props={"deleted_workspaces": deleted_workspaces}
            )

        result = WorkspaceService.create_workspace(name=name, user=request.user)

        if result.success:
            workspace = result.data
            request.session["active_workspace_id"] = str(workspace.id)
            messages.success(request, f"Workspace '{workspace.name}' created successfully!")
            return redirect(reverse("teams:workspace_settings", kwargs={"slug": workspace.slug}))
        else:
            messages.error(request, result.message or "Failed to create workspace")
            return redirect(reverse("teams:workspace_list"))


class WorkspaceSettingsView(LoginRequiredMixin, View):
    """لوحة التحكم بإعدادات مساحة العمل وإدارة الفريق."""

    login_url = "auth:login"

    def get(self, request, slug):
        workspace = get_object_or_404(Workspace, slug=slug)

        # التحقق من أن المستخدم عضو في مساحة العمل باستخدام الـ Selector
        membership = get_workspace_membership(workspace, request.user)
        if not membership:
            messages.error(request, "You do not have access to this workspace.")
            return redirect(reverse("teams:workspace_list"))

        # جلب الأعضاء والدعوات المعلقة باستخدام الـ Selectors المخصصة والمنسقة
        members = [
            {
                "id": str(m.id),
                "email": m.user.email,
                "role": m.role,
                "role_display": m.get_role_display(),
                "avatar_url": m.user.avatar_url
                or f"https://ui-avatars.com/api/?name={m.user.email}&background=6366f1&color=fff",
                "joined_at": m.created_at.strftime("%Y-%m-%d"),
                "is_self": (m.user == request.user),
            }
            for m in list_workspace_members(workspace)
        ]

        invitations = [
            {
                "id": str(i.id),
                "token": str(i.token),
                "email": i.email,
                "role": i.role,
                "role_display": i.get_role_display(),
                "status": i.status,
                "status_display": i.get_status_display(),
                "expires_at": i.expires_at.strftime("%Y-%m-%d"),
            }
            for i in list_workspace_pending_invitations(workspace)
        ]

        return render(
            request,
            "Teams/WorkspaceSettings",
            props={
                "workspace": {
                    "id": str(workspace.id),
                    "name": workspace.name,
                    "slug": workspace.slug,
                    "role": membership.role,
                },
                "members": members,
                "invitations": invitations,
            },
        )

    def post(self, request, slug):
        workspace = get_object_or_404(Workspace, slug=slug)

        # التحقق من الصلاحيات (Owner/Admin فقط) باستخدام الـ Selector
        membership = get_workspace_membership(workspace, request.user)
        if not membership or membership.role not in [
            WorkspaceMember.RoleChoices.OWNER,
            WorkspaceMember.RoleChoices.ADMIN,
        ]:
            messages.error(request, "Access denied. Only Owners and Admins can update settings.")
            return redirect(reverse("teams:workspace_settings", kwargs={"slug": slug}))

        data = get_request_data(request)
        name = data.get("name", "").strip()

        if not name:
            share(request, errors={"name": ["Workspace name is required"]})
            members = [
                {
                    "id": str(m.id),
                    "email": m.user.email,
                    "role": m.role,
                    "role_display": m.get_role_display(),
                    "avatar_url": m.user.avatar_url
                    or f"https://ui-avatars.com/api/?name={m.user.email}&background=6366f1&color=fff",
                    "joined_at": m.created_at.strftime("%Y-%m-%d"),
                    "is_self": (m.user == request.user),
                }
                for m in list_workspace_members(workspace)
            ]
            invitations = [
                {
                    "id": str(i.id),
                    "token": str(i.token),
                    "email": i.email,
                    "role": i.role,
                    "role_display": i.get_role_display(),
                    "status": i.status,
                    "status_display": i.get_status_display(),
                    "expires_at": i.expires_at.strftime("%Y-%m-%d"),
                }
                for i in list_workspace_pending_invitations(workspace)
            ]
            return render(
                request,
                "Teams/WorkspaceSettings",
                props={
                    "workspace": {
                        "id": str(workspace.id),
                        "name": workspace.name,
                        "slug": workspace.slug,
                        "role": membership.role,
                    },
                    "members": members,
                    "invitations": invitations,
                },
            )

        try:
            workspace.name = name
            # إذا رغبنا في تغيير الـ slug يدوياً (اختياري)
            new_slug = data.get("slug", "").strip()
            if new_slug and new_slug != workspace.slug:
                # توليد الـ slug الفريد والتحقق منه
                from django.utils.text import slugify

                base_slug = slugify(new_slug, allow_unicode=True)
                if base_slug:
                    test_slug = base_slug
                    counter = 1
                    queryset = Workspace.objects.exclude(pk=workspace.pk)
                    while queryset.filter(slug=test_slug).exists():
                        test_slug = f"{base_slug}-{counter}"
                        counter += 1
                    workspace.slug = test_slug

            workspace.save()
            messages.success(request, "Workspace settings updated successfully!")
            return redirect(reverse("teams:workspace_settings", kwargs={"slug": workspace.slug}))
        except Exception as e:
            messages.error(request, f"Failed to update workspace: {str(e)}")
            return redirect(reverse("teams:workspace_settings", kwargs={"slug": slug}))


class WorkspaceActiveSwitchView(LoginRequiredMixin, View):
    """تبديل مساحة العمل النشطة للمستخدم في الـ Session."""

    login_url = "auth:login"

    def post(self, request):
        data = get_request_data(request)
        workspace_id = data.get("workspace_id")

        if not workspace_id:
            return JsonResponse({"error": "workspace_id is required"}, status=400)

        # التحقق من العضوية
        membership = WorkspaceMember.objects.filter(
            workspace_id=workspace_id, user=request.user
        ).first()
        if not membership:
            return JsonResponse({"error": "You do not belong to this workspace"}, status=403)

        request.session["active_workspace_id"] = str(workspace_id)
        messages.success(request, f"Switched to workspace '{membership.workspace.name}'")

        # إرجاع رد لتوجيه الصفحة
        return redirect(reverse("profile"))


class WorkspaceInviteView(LoginRequiredMixin, View):
    """إرسال دعوة لعضو جديد للانضمام للفريق."""

    login_url = "auth:login"

    def post(self, request, slug):
        workspace = get_object_or_404(Workspace, slug=slug)
        data = get_request_data(request)
        email = data.get("email", "").strip()
        role = data.get("role", "MEMBER")

        result = WorkspaceService.invite_member(
            workspace=workspace, invited_by=request.user, email=email, role=role
        )

        if result.success:
            messages.success(request, result.message)
        else:
            messages.error(request, result.message)

        return redirect(reverse("teams:workspace_settings", kwargs={"slug": slug}))


class WorkspaceMemberDeleteView(LoginRequiredMixin, View):
    """حذف عضو من الفريق أو مغادرة مساحة العمل."""

    login_url = "auth:login"

    def post(self, request, slug, member_id):
        workspace = get_object_or_404(Workspace, slug=slug)

        # جلب معرف المستخدم قبل حذفه من قاعدة البيانات لمعرفة ما إذا كان يغادر بنفسه
        member_user_id = (
            WorkspaceMember.objects.filter(id=member_id, workspace=workspace)
            .values_list("user_id", flat=True)
            .first()
        )

        result = WorkspaceService.remove_member(
            workspace=workspace, member_id=member_id, operator=request.user
        )

        if result.success:
            messages.success(request, result.message)
            if member_user_id == request.user.id:
                return redirect(reverse("teams:workspace_list"))
        else:
            messages.error(request, result.message)

        return redirect(reverse("teams:workspace_settings", kwargs={"slug": slug}))


class WorkspaceMemberUpdateView(LoginRequiredMixin, View):
    """تعديل رتبة عضو في الفريق."""

    login_url = "auth:login"

    def post(self, request, slug, member_id):
        workspace = get_object_or_404(Workspace, slug=slug)
        data = get_request_data(request)
        role = data.get("role")

        result = WorkspaceService.update_member_role(
            workspace=workspace, member_id=member_id, new_role=role, operator=request.user
        )

        if result.success:
            messages.success(request, result.message)
        else:
            messages.error(request, result.message)

        return redirect(reverse("teams:workspace_settings", kwargs={"slug": slug}))


class WorkspaceInvitationAcceptView(View):
    """قبول دعوة الانضمام عبر الرابط الموقع بالتوكن."""

    def get(self, request, token):
        # 1. التحقق من وجود الدعوة
        invitation = get_object_or_404(WorkspaceInvitation, token=token)

        # 2. التحقق من مصادقة المستخدم الحالي
        if not request.user.is_authenticated:
            # الاحتفاظ بالتوكن في الجلسة ليتم القبول التلقائي بعد التسجيل/الدخول
            request.session["pending_invite_token"] = str(token)
            messages.info(
                request,
                (
                    f"Please log in or register to accept the invitation to "
                    f"join '{invitation.workspace.name}'."
                ),
            )
            return redirect(reverse("auth:login") + f"?next={request.path}")

        # 3. معالجة قبول الدعوة
        result = WorkspaceService.accept_invitation(token_uuid=invitation.token, user=request.user)

        if result.success:
            # تعيين مساحة العمل المقبولة كنشطة في الجلسة
            request.session["active_workspace_id"] = str(invitation.workspace.id)
            messages.success(request, result.message)
            return redirect(
                reverse("teams:workspace_settings", kwargs={"slug": invitation.workspace.slug})
            )
        else:
            messages.error(request, result.message)
            return redirect(reverse("teams:workspace_list"))


class WorkspaceInvitationDeleteView(LoginRequiredMixin, View):
    """إلغاء دعوة معلقة للإنضمام للفريق."""

    login_url = "auth:login"

    def post(self, request, slug, invitation_id):
        workspace = get_object_or_404(Workspace, slug=slug)

        # التحقق من الصلاحيات (Owner/Admin فقط) باستخدام الـ Selector
        membership = get_workspace_membership(workspace, request.user)
        if not membership or membership.role not in [
            WorkspaceMember.RoleChoices.OWNER,
            WorkspaceMember.RoleChoices.ADMIN,
        ]:
            messages.error(request, "Access denied. Only Owners and Admins can revoke invitations.")
            return redirect(reverse("teams:workspace_settings", kwargs={"slug": slug}))

        invitation = get_object_or_404(WorkspaceInvitation, id=invitation_id, workspace=workspace)
        invitation.delete()
        messages.success(request, "Invitation revoked successfully.")
        return redirect(reverse("teams:workspace_settings", kwargs={"slug": slug}))


class WorkspaceDeleteView(LoginRequiredMixin, View):
    """حذف مساحة العمل حذفاً ناعماً."""

    login_url = "auth:login"

    def post(self, request, slug):
        workspace = get_object_or_404(Workspace, slug=slug)
        result = WorkspaceService.delete_workspace(workspace=workspace, operator=request.user)

        if result.success:
            messages.success(request, result.message)
            # إذا تم حذف مساحة العمل النشطة، نقوم بإزالتها من الجلسة
            if str(workspace.id) == request.session.get("active_workspace_id"):
                request.session.pop("active_workspace_id", None)
            return redirect(reverse("teams:workspace_list"))
        else:
            messages.error(request, result.message)
            return redirect(reverse("teams:workspace_settings", kwargs={"slug": slug}))


class WorkspaceRestoreView(LoginRequiredMixin, View):
    """استرجاع مساحة العمل المحذوفة ناعماً."""

    login_url = "auth:login"

    def post(self, request, workspace_id):
        result = WorkspaceService.restore_workspace(
            workspace_id=workspace_id, operator=request.user
        )

        if result.success:
            messages.success(request, result.message)
            workspace = result.data
            request.session["active_workspace_id"] = str(workspace.id)
            return redirect(reverse("teams:workspace_settings", kwargs={"slug": workspace.slug}))
        else:
            messages.error(request, result.message)
            return redirect(reverse("teams:workspace_list"))
