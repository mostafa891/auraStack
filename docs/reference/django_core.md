# 🏛️ Django Core Architecture Guide

This document describes the core Django components, architecture, and configurations specifically implemented in the **AuraFlow** SaaS boilerplate.

---

## 📂 Project Structure & Settings

AuraFlow separates configurations logically under the `core/settings/` directory:
- `base.py`: The foundation settings shared by all environments.
- `local.py`: Local development overrides (e.g. debug mode, sqlite database).
- `production.py`: Hardened settings suitable for production deployment.

### Key Base Configurations
- **Custom User Model**: Enabled via `AUTH_USER_MODEL = "users.CustomUser"`.
- **Inertia Layout**: Root layout defined via `INERTIA_LAYOUT = "base.html"`.
- **Vite Integration**: Django-Vite is configured with a manifest path pointing to `static/dist/.vite/manifest.json`.

---

## 🗃️ Custom User Model & ORM

Instead of Django's default `username`-based model, AuraFlow implements a modern, secure, `email`-based custom user model in `apps/users/models.py`.

### Model: `CustomUser`
The [CustomUser](../../apps/users/models.py) class inherits from Django's `AbstractUser` and `TimeStampedModel` from `common/models.py`.

Key architecture choices:
1. **Primary Key**: Uses `UUIDField` (`uuid.uuid4`) for security and predictability in distributed contexts.
2. **Username Omitted**: `username = None` and `USERNAME_FIELD = "email"` ensuring email is the primary unique identifier.
3. **Preferences**:
   - `theme`: Choice of `LIGHT`, `DARK`, or `SYSTEM`.
   - `language`: TextChoice field supporting `en` (English) and `ar` (Arabic).
   - `timezone`: IANA-certified timezone strings mapped using Python's `zoneinfo` module.

### Manager: `CustomUserManager`
Defines helper functions to create users without needing a username field:
- `create_user(email, password, **extra_fields)`: Normalizes the email, sets the password securely, and saves to database.
- `create_superuser(email, password, **extra_fields)`: Forces `is_staff`, `is_superuser`, and `is_active` to `True`.

---

## ⛓️ Middleware Lifecycle

AuraFlow relies on a specific ordering of middleware classes in `base.py` to ensure proper authentication context is available for Inertia shares:

```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "inertia.middleware.InertiaMiddleware",
    "common.middleware.ShareUserDataMiddleware", # Custom middleware
]
```

### Custom Middleware: `ShareUserDataMiddleware`
Located in [common/middleware.py](../../common/middleware.py), this middleware shares key user metadata and workspace state with Vue:
- **`auth.user`**: Authenticated user details (`id`, `email`, `language`, `theme`, `timezone`, etc.).
- **`auth.workspaces`**: List of all workspaces the authenticated user belongs to (with their membership roles: `OWNER`, `ADMIN`, `MEMBER`).
- **`auth.active_workspace`**: The currently selected/active workspace from the session, defaulting to the first workspace if not set.
- **`flash`**: Django flash messages for displaying beautiful instant toast notifications.

This makes user profile, active tenancy context, and notification messages globally accessible as reactive props in Vue 3 pages.
