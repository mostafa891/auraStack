import uuid
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from apps.teams.models import Workspace, WorkspaceInvitation, WorkspaceMember
from common.results import ServiceResult


class WorkspaceService:
    """Workspace service layer managing business logic, tenant isolation, and security constraints."""

    @staticmethod
    def create_workspace(name: str, user) -> ServiceResult:
        """Creates a new workspace instance and assigns the creating user as OWNER."""
        if not name or not name.strip():
            return ServiceResult(success=False, message="Workspace name cannot be empty")

        try:
            with transaction.atomic():
                workspace = Workspace.objects.create(name=name.strip(), created_by=user)
                WorkspaceMember.objects.create(
                    workspace=workspace, user=user, role=WorkspaceMember.RoleChoices.OWNER
                )
            return ServiceResult(
                success=True, data=workspace, message="Workspace created successfully"
            )
        except Exception as e:
            return ServiceResult(success=False, message=f"Failed to create workspace: {str(e)}")

    @staticmethod
    def invite_member(workspace: Workspace, invited_by, email: str, role: str) -> ServiceResult:
        """Invites a new member to a workspace via email with duplicate checks."""
        email_clean = email.strip().lower()
        if not email_clean:
            return ServiceResult(success=False, message="Email address is required")

        if role not in WorkspaceMember.RoleChoices.values:
            return ServiceResult(success=False, message="Invalid role specified")

        # 1. Verify inviter permission (Must be OWNER or ADMIN)
        operator = WorkspaceMember.objects.filter(workspace=workspace, user=invited_by).first()
        if not operator or operator.role not in [
            WorkspaceMember.RoleChoices.OWNER,
            WorkspaceMember.RoleChoices.ADMIN,
        ]:
            return ServiceResult(
                success=False,
                message="Access denied. You do not have permission to invite members.",
            )

        # 2. Check if target user is already a member
        if workspace.members.filter(user__email__iexact=email_clean).exists():
            return ServiceResult(
                success=False, message="User is already a member of this workspace"
            )

        # 3. Check for active pending invitation for target email
        active_invite = workspace.invitations.filter(
            email__iexact=email_clean,
            status=WorkspaceInvitation.StatusChoices.PENDING,
            expires_at__gt=timezone.now(),
        ).exists()
        if active_invite:
            return ServiceResult(
                success=False, message="An active invitation has already been sent to this email"
            )

        # 4. Check plan member limit constraints
        from apps.payments.selectors import get_plan_limit

        max_members = get_plan_limit(workspace, "max_members")
        if max_members is not None:
            current_count = workspace.members.count()
            if current_count >= max_members:
                return ServiceResult(
                    success=False,
                    message=(
                        f"Your workspace has reached the maximum of {max_members} members "
                        f"for your current plan. Upgrade to add more members."
                    ),
                )

        # 5. Create invitation instance
        from django.conf import settings
        from django.core.mail import send_mail
        from django.template.loader import render_to_string

        expires_at = timezone.now() + timedelta(days=7)
        try:
            with transaction.atomic():
                invitation = WorkspaceInvitation.objects.create(
                    workspace=workspace,
                    email=email_clean,
                    role=role,
                    invited_by=invited_by,
                    expires_at=expires_at,
                )

                # Compose invite email message
                site_url = getattr(settings, "SITE_URL", "http://localhost:8000")
                invite_url = f"{site_url}/workspaces/invitations/{invitation.token}/accept/"

                context = {
                    "inviter": invited_by.email,
                    "workspace_name": workspace.name,
                    "invite_url": invite_url,
                }
                html_message = render_to_string("emails/workspace_invite.html", context)

                send_mail(
                    subject=f"Invitation to join team {workspace.name} on auraStack",
                    message=(
                        f"You have been invited by {invited_by.email} to join the "
                        f"{workspace.name} workspace. Accept here: {invite_url}"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email_clean],
                    html_message=html_message,
                )

            return ServiceResult(
                success=True,
                data=invitation,
                message=f"Invitation sent to {email_clean} successfully",
            )
        except Exception as e:
            return ServiceResult(success=False, message=f"Failed to create invitation: {str(e)}")

    @staticmethod
    def accept_invitation(token_uuid: uuid.UUID, user) -> ServiceResult:
        """Accepts invitation token and adds user to workspace with specified role."""
        invitation = WorkspaceInvitation.objects.filter(token=token_uuid).first()
        if not invitation:
            return ServiceResult(success=False, message="Invalid invitation link")

        # Verify status and expiration
        if (
            invitation.status != WorkspaceInvitation.StatusChoices.PENDING
            or invitation.expires_at <= timezone.now()
        ):
            if invitation.status == WorkspaceInvitation.StatusChoices.PENDING:
                invitation.status = WorkspaceInvitation.StatusChoices.EXPIRED
                invitation.save()
            return ServiceResult(
                success=False, message="This invitation has expired or is no longer valid"
            )

        # Verify email match
        if invitation.email.lower() != user.email.lower():
            return ServiceResult(
                success=False,
                message=(
                    f"This invitation was sent to {invitation.email}, "
                    f"but you are logged in as {user.email}"
                ),
            )

        # Verify user is not already a member
        existing_member = WorkspaceMember.objects.filter(
            workspace=invitation.workspace, user=user
        ).first()
        if existing_member:
            invitation.status = WorkspaceInvitation.StatusChoices.ACCEPTED
            invitation.save()
            return ServiceResult(
                success=True,
                data=existing_member,
                message="You are already a member of this workspace",
            )

        try:
            with transaction.atomic():
                member = WorkspaceMember.objects.create(
                    workspace=invitation.workspace, user=user, role=invitation.role
                )
                invitation.status = WorkspaceInvitation.StatusChoices.ACCEPTED
                invitation.save()
            return ServiceResult(
                success=True,
                data=member,
                message=f"Joined {invitation.workspace.name} successfully",
            )
        except Exception as e:
            return ServiceResult(success=False, message=f"Failed to join workspace: {str(e)}")

    @staticmethod
    def remove_member(workspace: Workspace, member_id: str, operator) -> ServiceResult:
        """Removes a workspace member enforcing role hierarchy and sole owner safeguards."""
        member = WorkspaceMember.objects.filter(id=member_id, workspace=workspace).first()
        if not member:
            return ServiceResult(success=False, message="Member not found in this workspace")

        # Get operator membership role
        operator_member = WorkspaceMember.objects.filter(workspace=workspace, user=operator).first()
        if not operator_member:
            return ServiceResult(
                success=False, message="Access denied. You are not a member of this workspace."
            )

        is_self = member.user == operator

        # 1. Handle self-removal / leaving workspace
        if is_self:
            if member.role == WorkspaceMember.RoleChoices.OWNER:
                # Prevent sole owner from leaving without assigning another owner
                owners_count = workspace.members.filter(
                    role=WorkspaceMember.RoleChoices.OWNER
                ).count()
                if owners_count <= 1:
                    return ServiceResult(
                        success=False,
                        message=(
                            "You are the only Owner. You must promote another member "
                            "to Owner before leaving, or delete the workspace."
                        ),
                    )
            member.delete()
            return ServiceResult(success=True, message="You have left the workspace successfully")

        # 2. Handle removing another member
        if operator_member.role not in [
            WorkspaceMember.RoleChoices.OWNER,
            WorkspaceMember.RoleChoices.ADMIN,
        ]:
            return ServiceResult(
                success=False, message="Access denied. Only Owners and Admins can remove members."
            )

        # ADMIN cannot remove OWNER or another ADMIN
        if operator_member.role == WorkspaceMember.RoleChoices.ADMIN:
            if member.role in [
                WorkspaceMember.RoleChoices.OWNER,
                WorkspaceMember.RoleChoices.ADMIN,
            ]:
                return ServiceResult(
                    success=False,
                    message="Access denied. Admins cannot remove Owners or other Admins.",
                )

        member.delete()
        return ServiceResult(
            success=True, message=f"Member {member.user.email} removed successfully"
        )

    @staticmethod
    def update_member_role(
        workspace: Workspace, member_id: str, new_role: str, operator
    ) -> ServiceResult:
        """Updates workspace member role protecting sole owner role."""
        if new_role not in WorkspaceMember.RoleChoices.values:
            return ServiceResult(success=False, message="Invalid role specified")

        member = WorkspaceMember.objects.filter(id=member_id, workspace=workspace).first()
        if not member:
            return ServiceResult(success=False, message="Member not found in this workspace")

        operator_member = WorkspaceMember.objects.filter(workspace=workspace, user=operator).first()
        if not operator_member:
            return ServiceResult(
                success=False, message="Access denied. You are not a member of this workspace."
            )

        # 1. Prevent demoting sole owner
        if (
            member.role == WorkspaceMember.RoleChoices.OWNER
            and new_role != WorkspaceMember.RoleChoices.OWNER
        ):
            owners_count = workspace.members.filter(role=WorkspaceMember.RoleChoices.OWNER).count()
            if owners_count <= 1:
                return ServiceResult(
                    success=False,
                    message=(
                        "This member is the only Owner. Promote another member "
                        "to Owner before changing their role."
                    ),
                )

        # 2. Check operator permissions
        if operator_member.role not in [
            WorkspaceMember.RoleChoices.OWNER,
            WorkspaceMember.RoleChoices.ADMIN,
        ]:
            return ServiceResult(
                success=False, message="Access denied. Only Owners and Admins can change roles."
            )

        # ADMIN cannot promote or demote OWNER/ADMIN roles
        if operator_member.role == WorkspaceMember.RoleChoices.ADMIN:
            if member.role in [
                WorkspaceMember.RoleChoices.OWNER,
                WorkspaceMember.RoleChoices.ADMIN,
            ] or new_role in [WorkspaceMember.RoleChoices.OWNER, WorkspaceMember.RoleChoices.ADMIN]:
                return ServiceResult(
                    success=False, message="Access denied. Admins cannot modify Owner/Admin roles."
                )

        member.role = new_role
        member.save()
        return ServiceResult(
            success=True,
            data=member,
            message=f"Role updated to {member.get_role_display()} successfully",
        )

    @staticmethod
    def delete_workspace(workspace: Workspace, operator) -> ServiceResult:
        """Soft-deletes workspace verifying OWNER permission."""
        operator_member = WorkspaceMember.objects.filter(workspace=workspace, user=operator).first()
        if not operator_member or operator_member.role != WorkspaceMember.RoleChoices.OWNER:
            return ServiceResult(
                success=False, message="Access denied. Only the Owner can delete this workspace."
            )
        try:
            with transaction.atomic():
                workspace.delete()
                WorkspaceMember.objects.filter(workspace=workspace).delete()
            return ServiceResult(success=True, message="Workspace archived successfully.")
        except Exception as e:
            return ServiceResult(success=False, message=f"Failed to delete workspace: {str(e)}")

    @staticmethod
    def restore_workspace(workspace_id: str, operator) -> ServiceResult:
        """Restores soft-deleted workspace verifying OWNER permission."""
        try:
            workspace = Workspace.all_objects.filter(
                id=workspace_id, deleted_at__isnull=False
            ).first()
            if not workspace:
                return ServiceResult(success=False, message="Workspace not found or not archived.")

            operator_member = WorkspaceMember.all_objects.filter(
                workspace=workspace, user=operator, role=WorkspaceMember.RoleChoices.OWNER
            ).first()
            if not operator_member:
                return ServiceResult(
                    success=False,
                    message="Access denied. Only the Owner can restore this workspace.",
                )

            with transaction.atomic():
                workspace.deleted_at = None
                workspace.save(update_fields=["deleted_at"])
                WorkspaceMember.all_objects.filter(workspace=workspace).update(deleted_at=None)

            return ServiceResult(
                success=True, data=workspace, message="Workspace restored successfully."
            )
        except Exception as e:
            return ServiceResult(success=False, message=f"Failed to restore workspace: {str(e)}")
