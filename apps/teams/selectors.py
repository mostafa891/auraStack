from apps.teams.models import Workspace, WorkspaceInvitation, WorkspaceMember


def list_user_workspaces(user) -> list[WorkspaceMember]:
    """Lists user workspace memberships efficiently joining workspace and subscription data."""
    if not user or not user.is_authenticated:
        return []
    return list(
        WorkspaceMember.objects.filter(user=user)
        .select_related("workspace", "workspace__subscription")
        .order_by("created_at")
    )


def get_active_workspace(user, active_workspace_id: str | None) -> WorkspaceMember | None:
    """Retrieves active workspace membership for user with prefetched subscription details."""
    if not user or not user.is_authenticated or not active_workspace_id:
        return None

    # Use select_related to optimize query performance and join workspace subscription
    return (
        WorkspaceMember.objects.filter(workspace_id=active_workspace_id, user=user)
        .select_related("workspace", "workspace__subscription")
        .first()
    )


def get_workspace_membership(workspace: Workspace, user) -> WorkspaceMember | None:
    """Retrieves membership for a specific user in a specific workspace."""
    if not user or not user.is_authenticated:
        return None
    return WorkspaceMember.objects.filter(workspace=workspace, user=user).first()


def list_workspace_members(workspace: Workspace) -> list[WorkspaceMember]:
    """Lists workspace members optimizing select_related to avoid N+1 query overhead."""
    return list(workspace.members.select_related("user").order_by("created_at"))


def list_workspace_pending_invitations(workspace: Workspace) -> list[WorkspaceInvitation]:
    """Lists pending invitations for a workspace."""
    return list(
        workspace.invitations.filter(status=WorkspaceInvitation.StatusChoices.PENDING).order_by(
            "-created_at"
        )
    )


def list_deleted_user_workspaces(user) -> list[Workspace]:
    """Lists soft-deleted workspaces created by the user."""
    if not user or not user.is_authenticated:
        return []
    return list(
        Workspace.all_objects.filter(created_by=user, deleted_at__isnull=False).order_by(
            "-deleted_at"
        )
    )
