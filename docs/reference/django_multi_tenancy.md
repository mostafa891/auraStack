# 🏢 Multi-tenancy & Workspace (Teams) Guide

This guide documents the Multi-tenancy architecture implemented in AuraFlow under the `apps.teams` application. It details how workspaces, memberships, and invitations are managed across the database, services, views, and Vue 3 frontend.

---

## 🏗️ Architecture Design

AuraFlow implements a **Shared Database, Shared Schema (Row-level Isolation)** multi-tenancy model. 
This is the industry standard for SaaS platforms like Slack, GitHub, or Notion, where:
1. Users register once and can belong to multiple workspaces.
2. Users can easily switch between their active workspaces in the UI.
3. Access control is scoped per workspace member and role.

---

## 🗃️ Models (`apps/teams/models.py`)

1. **`Workspace`**
   - Represents the tenant (organization, company, or project).
   - **Fields**: `id` (UUID primary key), `name` (CharField), `slug` (SlugField, unique), `created_by` (ForeignKey to user), and `created_at`/`updated_at`.
   - **Auto-slugification**: The model overrides `save()` to automatically generate a unique, URL-safe slug from the name. It uses Django's `slugify(allow_unicode=True)` to fully support Arabic names and handles duplicates by appending sequence numbers (e.g. `test-1`, `test-2`).

2. **`WorkspaceMember`**
   - Maps users to workspaces.
   - **Fields**: `workspace` (ForeignKey), `user` (ForeignKey), and `role` (CharField with choices `OWNER`, `ADMIN`, `MEMBER`).
   - **Constraints**: Enforces `unique_together = ("workspace", "user")` to prevent duplicate memberships.

3. **`WorkspaceInvitation`**
   - Manages team invitation flows.
   - **Fields**: `workspace` (ForeignKey), `email` (EmailField), `role` (CharField), `token` (UUID, unique), `invited_by` (ForeignKey), `status` (`PENDING`, `ACCEPTED`, `EXPIRED`), and `expires_at` (DateTimeField).

---

## ⚙️ Service Layer (`apps/teams/services.py`)

To decouple business rules from view controllers, all operations are handled inside the class-based **`WorkspaceService`**:

- **`create_workspace(name, user)`**: Spawns a new workspace and automatically adds the creator as `OWNER`.
- **`invite_member(workspace, invited_by, email, role)`**: Creates a pending invitation if the user is not already a member and no active pending invitation exists.
- **`accept_invitation(token, user)`**: Adds the user to the workspace with the designated role and sets the invitation status to `ACCEPTED`.
- **`remove_member(workspace, member_id, operator)`**: Expedites leaves and expulsions. Includes owner-protection logic (e.g. a sole owner cannot leave the workspace).
- **`update_member_role(workspace, member_id, new_role, operator)`**: Alters a member's privileges. Prevents demoting the sole owner.

---

## 🔗 Views, Routing & Context Switching

The application routes are registered under the `/workspaces/` path prefix:
- `workspace_list` (`/workspaces/`): Lists workspaces and creates new ones.
- `workspace_switch` (`/workspaces/switch/`): Modifies `request.session['active_workspace_id']` to switch active contexts.
- `workspace_settings` (`/workspaces/<slug>/settings/`): Updates workspace details and acts as the member/invitation dashboard.
- `accept_invitation` (`/workspaces/invitations/<token>/accept/`): Links clicked from emails to accept invites.

---

## 🎨 Vue 3 Frontend Pages (`frontend/src/pages/Teams/`)

1. **`WorkspaceList.vue`**
   - An elegant interface displaying workspace cards with role badges.
   - Triggers context switching and houses the "Create Workspace" modal.

2. **`WorkspaceSettings.vue`**
   - The settings panel for admins/owners to update names/slugs, adjust roles, remove members, revoke invites, and send new email invitations.
   - Includes a "Copy Link" utility for copying invitation accept URLs for local development testing.

---

## 🧪 Testing

1. **Unit & Integration Tests**: Located in [test_teams.py](file:///a:/auraflow/apps/teams/tests/test_teams.py). Tests slug generation, services constraints, and basic view flow redirections. Run with:
   ```bash
   pytest apps/teams/tests/
   ```
2. **E2E Browser Tests**: Located in [test_teams_flow.py](file:///a:/auraflow/tests/e2e/test_teams_flow.py). Tests registration, workspace creation, settings page, and invitation workflows. Run with:
   ```bash
   pytest tests/e2e/
   ```
