from apps.teams.models import Workspace, WorkspaceInvitation, WorkspaceMember


def list_user_workspaces(user) -> list[WorkspaceMember]:
    """جلب قائمة عضويات مساحات العمل للمستخدم بكفاءة مع الانضمام لبيانات مساحة العمل."""
    if not user or not user.is_authenticated:
        return []
    return list(
        WorkspaceMember.objects.filter(user=user).select_related("workspace").order_by("created_at")
    )


def get_active_workspace(user, active_workspace_id: str | None) -> WorkspaceMember | None:
    """جلب عضوية مساحة العمل النشطة الحالية للمستخدم."""
    if not user or not user.is_authenticated or not active_workspace_id:
        return None

    # استخدام select_related للتخزين المؤقت وحقن الكائن
    return (
        WorkspaceMember.objects.filter(workspace_id=active_workspace_id, user=user)
        .select_related("workspace")
        .first()
    )


def get_workspace_membership(workspace: Workspace, user) -> WorkspaceMember | None:
    """جلب عضوية مستخدم محدد في مساحة عمل محددة."""
    if not user or not user.is_authenticated:
        return None
    return WorkspaceMember.objects.filter(workspace=workspace, user=user).first()


def list_workspace_members(workspace: Workspace) -> list[WorkspaceMember]:
    """جلب قائمة أعضاء مساحة العمل بشكل محسن لتقليل استعلامات N+1 للمستخدمين."""
    return list(workspace.members.select_related("user").order_by("created_at"))


def list_workspace_pending_invitations(workspace: Workspace) -> list[WorkspaceInvitation]:
    """جلب قائمة الدعوات المعلقة لمساحة العمل."""
    return list(
        workspace.invitations.filter(status=WorkspaceInvitation.StatusChoices.PENDING).order_by(
            "-created_at"
        )
    )


def list_deleted_user_workspaces(user) -> list[Workspace]:
    """جلب قائمة مساحات العمل المحذوفة ناعماً والتي أنشأها المستخدم."""
    if not user or not user.is_authenticated:
        return []
    return list(
        Workspace.all_objects.filter(created_by=user, deleted_at__isnull=False).order_by(
            "-deleted_at"
        )
    )
