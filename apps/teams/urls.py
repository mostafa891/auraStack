from django.urls import path

from apps.teams.views import (
    WorkspaceActiveSwitchView,
    WorkspaceInvitationAcceptView,
    WorkspaceInvitationDeleteView,
    WorkspaceInviteView,
    WorkspaceListView,
    WorkspaceMemberDeleteView,
    WorkspaceMemberUpdateView,
    WorkspaceSettingsView,
)

app_name = "teams"

urlpatterns = [
    path("", WorkspaceListView.as_view(), name="workspace_list"),
    path("switch/", WorkspaceActiveSwitchView.as_view(), name="workspace_switch"),
    path("<slug:slug>/settings/", WorkspaceSettingsView.as_view(), name="workspace_settings"),
    path("<slug:slug>/invite/", WorkspaceInviteView.as_view(), name="workspace_invite"),
    path(
        "<slug:slug>/members/<uuid:member_id>/delete/",
        WorkspaceMemberDeleteView.as_view(),
        name="workspace_member_delete",
    ),
    path(
        "<slug:slug>/members/<uuid:member_id>/update/",
        WorkspaceMemberUpdateView.as_view(),
        name="workspace_member_update",
    ),
    path(
        "<slug:slug>/invitations/<uuid:invitation_id>/delete/",
        WorkspaceInvitationDeleteView.as_view(),
        name="workspace_invitation_delete",
    ),
    path(
        "invitations/<uuid:token>/accept/",
        WorkspaceInvitationAcceptView.as_view(),
        name="accept_invitation",
    ),
]
