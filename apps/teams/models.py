import uuid

from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from common.models import TimeStampedModel


class Workspace(TimeStampedModel):
    """يمثل مساحة العمل أو المستأجر (Tenant) الرئيسي في المنصة."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("workspace name"), max_length=100)
    slug = models.SlugField(_("slug"), max_length=100, unique=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_workspaces",
        verbose_name=_("created by"),
    )

    class Meta:
        verbose_name = _("workspace")
        verbose_name_plural = _("workspaces")
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            # توليد slug مبدئي يدعم اللغة العربية
            base_slug = slugify(self.name, allow_unicode=True)
            if not base_slug:
                # إذا كان الاسم يحتوي على رموز خاصة فقط أو فارغ، نستخدم معرّف عشوائي قصير
                base_slug = f"workspace-{uuid.uuid4().hex[:6]}"

            slug = base_slug
            counter = 1
            queryset = Workspace.objects.all()
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)

            while queryset.filter(slug=slug).exists():
                max_len = 100 - len(str(counter)) - 1
                slug = f"{base_slug[:max_len]}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class WorkspaceMember(TimeStampedModel):
    """يربط المستخدمين بمساحات العمل مع تحديد رتبهم وصلاحياتهم."""

    class RoleChoices(models.TextChoices):
        OWNER = "OWNER", _("Owner")
        ADMIN = "ADMIN", _("Admin")
        MEMBER = "MEMBER", _("Member")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="members",
        verbose_name=_("workspace"),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="workspace_memberships",
        verbose_name=_("user"),
    )
    role = models.CharField(
        _("role"),
        max_length=20,
        choices=RoleChoices.choices,
        default=RoleChoices.MEMBER,
    )

    class Meta:
        verbose_name = _("workspace member")
        verbose_name_plural = _("workspace members")
        unique_together = ("workspace", "user")
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"{self.user.email} in {self.workspace.name} ({self.get_role_display()})"


class WorkspaceInvitation(TimeStampedModel):
    """إدارة دعوات البريد الإلكتروني للانضمام لمساحات العمل."""

    class StatusChoices(models.TextChoices):
        PENDING = "PENDING", _("Pending")
        ACCEPTED = "ACCEPTED", _("Accepted")
        EXPIRED = "EXPIRED", _("Expired")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="invitations",
        verbose_name=_("workspace"),
    )
    email = models.EmailField(_("invited email"))
    role = models.CharField(
        _("role"),
        max_length=20,
        choices=WorkspaceMember.RoleChoices.choices,
        default=WorkspaceMember.RoleChoices.MEMBER,
    )
    token = models.UUIDField(_("invitation token"), default=uuid.uuid4, unique=True, editable=False)
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_invitations",
        verbose_name=_("invited by"),
    )
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
    )
    expires_at = models.DateTimeField(_("expires at"))

    class Meta:
        verbose_name = _("workspace invitation")
        verbose_name_plural = _("workspace invitations")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Invite for {self.email} to {self.workspace.name}"
