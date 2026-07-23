import uuid
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from apps.teams.models import Workspace, WorkspaceInvitation, WorkspaceMember
from common.results import ServiceResult


class WorkspaceService:
    """طبقة الخدمات لإدارة الأعمال والتحقق الأمني لمساحات العمل والفرق."""

    @staticmethod
    def create_workspace(name: str, user) -> ServiceResult:
        """إنشاء مساحة عمل جديدة وإضافة المستخدم كمالك (OWNER) لها."""
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
        """دعوة عضو جديد لمساحة العمل عبر البريد الإلكتروني مع التحقق من عدم تكراره."""
        email_clean = email.strip().lower()
        if not email_clean:
            return ServiceResult(success=False, message="Email address is required")

        if role not in WorkspaceMember.RoleChoices.values:
            return ServiceResult(success=False, message="Invalid role specified")

        # 1. التحقق من صلاحية الداعي (يجب أن يكون OWNER أو ADMIN)
        operator = WorkspaceMember.objects.filter(workspace=workspace, user=invited_by).first()
        if not operator or operator.role not in [
            WorkspaceMember.RoleChoices.OWNER,
            WorkspaceMember.RoleChoices.ADMIN,
        ]:
            return ServiceResult(
                success=False,
                message="Access denied. You do not have permission to invite members.",
            )

        # 2. التحقق من أن المستخدم ليس عضواً بالفعل
        if workspace.members.filter(user__email__iexact=email_clean).exists():
            return ServiceResult(
                success=False, message="User is already a member of this workspace"
            )

        # 3. التحقق من وجود دعوة معلقة صالحة لنفس البريد
        active_invite = workspace.invitations.filter(
            email__iexact=email_clean,
            status=WorkspaceInvitation.StatusChoices.PENDING,
            expires_at__gt=timezone.now(),
        ).exists()
        if active_invite:
            return ServiceResult(
                success=False, message="An active invitation has already been sent to this email"
            )

        # 4. التحقق من حد الأعضاء وفقاً للخطة المدفوعة
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

        # 5. إنشاء الدعوة
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

                # تجميع ورسالة البريد الإلكتروني
                site_url = getattr(settings, "SITE_URL", "http://localhost:8000")
                invite_url = f"{site_url}/workspaces/invitations/{invitation.token}/accept/"

                context = {
                    "inviter": invited_by.email,
                    "workspace_name": workspace.name,
                    "invite_url": invite_url,
                }
                html_message = render_to_string("emails/workspace_invite.html", context)

                send_mail(
                    subject=f"Invitation to join team {workspace.name} on AuraFlow",
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
        """قبول الدعوة وإضافة المستخدم كعضو بالصلاحية المحددة بالدعوة."""
        invitation = WorkspaceInvitation.objects.filter(token=token_uuid).first()
        if not invitation:
            return ServiceResult(success=False, message="Invalid invitation link")

        # التحقق من الصلاحية والوقت
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

        # التحقق من تطابق البريد الإلكتروني
        if invitation.email.lower() != user.email.lower():
            return ServiceResult(
                success=False,
                message=(
                    f"This invitation was sent to {invitation.email}, "
                    f"but you are logged in as {user.email}"
                ),
            )

        # التحقق من أن المستخدم ليس عضواً بالفعل
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
        """إزالة عضو من مساحة العمل مع التحقق من الصلاحيات والقيود الأمنية."""
        member = WorkspaceMember.objects.filter(id=member_id, workspace=workspace).first()
        if not member:
            return ServiceResult(success=False, message="Member not found in this workspace")

        # الحصول على دور المنفذ (Operator)
        operator_member = WorkspaceMember.objects.filter(workspace=workspace, user=operator).first()
        if not operator_member:
            return ServiceResult(
                success=False, message="Access denied. You are not a member of this workspace."
            )

        is_self = member.user == operator

        # 1. إذا كان يغادر بنفسه (Self-removal/Leave)
        if is_self:
            if member.role == WorkspaceMember.RoleChoices.OWNER:
                # التحقق من عدم كونه المالك الوحيد
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

        # 2. إذا كان المنفذ يزيل شخصاً آخر
        # التحقق من رتبة المنفذ
        if operator_member.role not in [
            WorkspaceMember.RoleChoices.OWNER,
            WorkspaceMember.RoleChoices.ADMIN,
        ]:
            return ServiceResult(
                success=False, message="Access denied. Only Owners and Admins can remove members."
            )

        # المشرف (ADMIN) لا يمكنه إزالة مالك (OWNER) أو مشرف آخر (ADMIN)
        if operator_member.role == WorkspaceMember.RoleChoices.ADMIN:
            if member.role in [
                WorkspaceMember.RoleChoices.OWNER,
                WorkspaceMember.RoleChoices.ADMIN,
            ]:
                return ServiceResult(
                    success=False,
                    message="Access denied. Admins cannot remove Owners or other Admins.",
                )

        # المالك (OWNER) يمكنه إزالة أي شخص عدا نفسه (تم معالجتها في Leave)
        member.delete()
        return ServiceResult(
            success=True, message=f"Member {member.user.email} removed successfully"
        )

    @staticmethod
    def update_member_role(
        workspace: Workspace, member_id: str, new_role: str, operator
    ) -> ServiceResult:
        """تعديل رتبة وصلاحيات العضو مع حماية رتبة المالك الوحيد."""
        if new_role not in WorkspaceMember.RoleChoices.values:
            return ServiceResult(success=False, message="Invalid role specified")

        member = WorkspaceMember.objects.filter(id=member_id, workspace=workspace).first()
        if not member:
            return ServiceResult(success=False, message="Member not found in this workspace")

        # الحصول على دور المنفذ (Operator)
        operator_member = WorkspaceMember.objects.filter(workspace=workspace, user=operator).first()
        if not operator_member:
            return ServiceResult(
                success=False, message="Access denied. You are not a member of this workspace."
            )

        # 1. لا يجوز تعديل رتبة المالك الوحيد إلى رتبة أقل
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

        # 2. التحقق من الصلاحيات الأمنية للمنفذ
        if operator_member.role not in [
            WorkspaceMember.RoleChoices.OWNER,
            WorkspaceMember.RoleChoices.ADMIN,
        ]:
            return ServiceResult(
                success=False, message="Access denied. Only Owners and Admins can change roles."
            )

        # المشرف (ADMIN) لا يمكنه ترقية أو تخفيض رتبة الملاك أو المشرفين
        if operator_member.role == WorkspaceMember.RoleChoices.ADMIN:
            if member.role in [
                WorkspaceMember.RoleChoices.OWNER,
                WorkspaceMember.RoleChoices.ADMIN,
            ] or new_role in [WorkspaceMember.RoleChoices.OWNER, WorkspaceMember.RoleChoices.ADMIN]:
                return ServiceResult(
                    success=False, message="Access denied. Admins cannot modify Owner/Admin roles."
                )

        # المالك (OWNER) يمكنه تغيير أي رتبة
        member.role = new_role
        member.save()
        return ServiceResult(
            success=True,
            data=member,
            message=f"Role updated to {member.get_role_display()} successfully",
        )

    @staticmethod
    def delete_workspace(workspace: Workspace, operator) -> ServiceResult:
        """حذف مساحة العمل حذفاً ناعماً والتحقق من صلاحية المالك (OWNER)."""
        operator_member = WorkspaceMember.objects.filter(workspace=workspace, user=operator).first()
        if not operator_member or operator_member.role != WorkspaceMember.RoleChoices.OWNER:
            return ServiceResult(
                success=False, message="Access denied. Only the Owner can delete this workspace."
            )
        try:
            with transaction.atomic():
                # الحذف الناعم لمساحة العمل
                workspace.delete()
                # الحذف الناعم لجميع الأعضاء المنتسبين إليها لكي يختفوا من لوحات التحكم
                WorkspaceMember.objects.filter(workspace=workspace).delete()
            return ServiceResult(success=True, message="Workspace archived successfully.")
        except Exception as e:
            return ServiceResult(success=False, message=f"Failed to delete workspace: {str(e)}")

    @staticmethod
    def restore_workspace(workspace_id: str, operator) -> ServiceResult:
        """استرجاع مساحة العمل المحذوفة ناعماً والتحقق من الصلاحيات."""
        try:
            # جلب مساحة العمل المحذوفة ناعماً عبر Manager المخصص
            workspace = Workspace.all_objects.filter(
                id=workspace_id, deleted_at__isnull=False
            ).first()
            if not workspace:
                return ServiceResult(success=False, message="Workspace not found or not archived.")

            # التحقق من أن المنفذ هو من أنشأ مساحة العمل أو كان المالك
            operator_member = WorkspaceMember.all_objects.filter(
                workspace=workspace, user=operator, role=WorkspaceMember.RoleChoices.OWNER
            ).first()
            if not operator_member:
                return ServiceResult(
                    success=False,
                    message="Access denied. Only the Owner can restore this workspace.",
                )

            with transaction.atomic():
                # إلغاء الحذف الناعم لمساحة العمل
                workspace.deleted_at = None
                workspace.save(update_fields=["deleted_at"])
                # استعادة عضويات جميع الأعضاء
                WorkspaceMember.all_objects.filter(workspace=workspace).update(deleted_at=None)

            return ServiceResult(
                success=True, data=workspace, message="Workspace restored successfully."
            )
        except Exception as e:
            return ServiceResult(success=False, message=f"Failed to restore workspace: {str(e)}")
