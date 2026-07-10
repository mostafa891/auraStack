from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.teams.models import Workspace, WorkspaceInvitation, WorkspaceMember


@admin.register(Workspace)
class WorkspaceAdmin(ModelAdmin):
    list_display = ("name", "slug", "created_by", "created_at")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("-created_at",)


@admin.register(WorkspaceMember)
class WorkspaceMemberAdmin(ModelAdmin):
    list_display = ("workspace", "user", "role", "created_at")
    list_filter = ("role", "workspace")
    search_fields = ("user__email", "workspace__name")
    ordering = ("-created_at",)


@admin.register(WorkspaceInvitation)
class WorkspaceInvitationAdmin(ModelAdmin):
    list_display = (
        "email",
        "workspace",
        "role",
        "status",
        "invited_by",
        "expires_at",
        "created_at",
    )
    list_filter = ("status", "role", "workspace")
    search_fields = ("email", "workspace__name")
    ordering = ("-created_at",)
