from django.urls import path

from apps.teams.views import (
    WorkspaceActiveSwitchView,
    WorkspaceDeleteView,
    WorkspaceInvitationAcceptView,
    WorkspaceInvitationDeleteView,
    WorkspaceInviteView,
    WorkspaceListView,
    WorkspaceMemberDeleteView,
    WorkspaceMemberUpdateView,
    WorkspaceRestoreView,
    WorkspaceSettingsView,
)

app_name = "teams"

urlpatterns = [
    path("", WorkspaceListView.as_view(), name="workspace_list"),
    path("switch/", WorkspaceActiveSwitchView.as_view(), name="workspace_switch"),
    path("<str:slug>/settings/", WorkspaceSettingsView.as_view(), name="workspace_settings"),
    path("<str:slug>/invite/", WorkspaceInviteView.as_view(), name="workspace_invite"),
    path(
        "<str:slug>/members/<uuid:member_id>/delete/",
        WorkspaceMemberDeleteView.as_view(),
        name="workspace_member_delete",
    ),
    path(
        "<str:slug>/members/<uuid:member_id>/update/",
        WorkspaceMemberUpdateView.as_view(),
        name="workspace_member_update",
    ),
    path(
        "<str:slug>/invitations/<uuid:invitation_id>/delete/",
        WorkspaceInvitationDeleteView.as_view(),
        name="workspace_invitation_delete",
    ),
    path(
        "invitations/<uuid:token>/accept/",
        WorkspaceInvitationAcceptView.as_view(),
        name="accept_invitation",
    ),
    path("<str:slug>/delete/", WorkspaceDeleteView.as_view(), name="workspace_delete"),
    path("<uuid:workspace_id>/restore/", WorkspaceRestoreView.as_view(), name="workspace_restore"),
]
