# Multi-Tenancy & Isolation

This document describes the multi-tenant architecture of AuraStack, explaining how workspaces are isolated and how member roles are managed.

---

## 🏢 1. Multi-Tenant Workspace Model
All core application data inside AuraStack belongs to a `Workspace`. Every user can belong to multiple workspaces, representing isolated organizations.

```
┌──────────────────────────────────────────────┐
│                    User                      │
└──────┬────────────────────────────────┬──────┘
       │                                │
┌──────▼──────┐                  ┌──────▼──────┐
│ Workspace A │                  │ Workspace B │
├─────────────┤                  ├─────────────┤
│ - Member A  │                  │ - Member C  │
│ - Member B  │                  │ - Member D  │
└─────────────┘                  └─────────────┘
```

*   **Database Isolation:** All business entities (transactions, subscriptions, features) hold a foreign key to `Workspace`. Queries are filtered by the active workspace to prevent cross-tenant data leakage.

---

## 👥 2. Membership & Roles
Users are linked to workspaces via the `WorkspaceMember` junction table, which defines their workspace-specific role:

| Role | Permissions |
| :--- | :--- |
| **OWNER** | Full administrative rights, managing subscriptions, deleting the workspace. |
| **ADMIN** | Managing team invitations, editing workspace details. |
| **MEMBER** | Read/write access to resources, cannot change settings or billing. |

---

## 🛡️ 3. BOLA / IDOR Prevention (Access Checking)
To prevent BOLA (Broken Object Level Authorization) attacks, workspace membership is checked on every API transaction.

*   **Middleware Verification:** The active workspace is loaded and attached to the request (`request.active_workspace`).
*   **Role Validation Helper:**
    ```python
    from apps.teams.selectors import get_workspace_membership
    
    # Verify user is OWNER or ADMIN in target workspace
    membership = get_workspace_membership(user=request.user, workspace=workspace)
    if membership.role not in [WorkspaceMember.RoleChoices.OWNER, WorkspaceMember.RoleChoices.ADMIN]:
        raise PermissionDenied("Access Denied")
    ```
*   **Security Outcome:** A user cannot alter another workspace's parameters simply by modifying the `workspace_id` UUID payload parameter.
