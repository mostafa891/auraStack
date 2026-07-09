# 📦 Installed Django Packages Reference

This document highlights the third-party Django libraries integrated into **AuraFlow** and explains their specific role and implementation patterns.

---

## ⚙️ Core Packages

### 1. `django-environ`
Handles configuration using environment variables from a `.env` file:
- **Usage**: Loaded in `base.py` to securely fetch secret credentials (like `SECRET_KEY`, databases, and allowed hosts).
- **Reference**:
  ```python
  import environ
  environ.Env.read_env(str(BASE_DIR / ".env"))
  env = environ.Env()
  ```

### 2. `django-vite`
Bridges the Django template renderer with Vite's asset compiler:
- **Usage**: Injects hot-reloading clients in development and reads the static assets compilation manifest files in production.

### 3. `django-allauth`
Manages the authentication, session state verification, password resets, Multi-Factor Authentication (MFA), and social account links.
- **Usage**: Backs the custom SPA security views and handles the underlying authentication database flows.

### 4. `django-unfold`
A modern, dark-mode styling layer for Django's built-in Admin console:
- **Usage**: Registered in `settings/base.py` and implemented inside `users/admin.py`.

---

## 🛠️ Utility Packages

### 1. `django-cleanup`
Cleans up the database file storage system automatically:
- **Usage**: Monitors user/profile models and deletes old avatar images from local storage when records are deleted or updated.

### 2. `django-extensions`
A collection of custom extensions for the Django Framework:
- **Usage**: Provides database and console utilities, notably the `runscript` CLI tool, which is used to populate test databases:
  ```bash
  python manage.py runscript seed_data
  ```

---

## ⚠️ Unused Dependencies Notice

The following packages are registered in `requirements.txt` but are **not** currently referenced by the project's source code:
- **`django-lifecycle`**: Provides decorator hooks for model events. Under our current architecture, lifecycle logic is handled cleanly by the Service Layer (`AuthService` in `services.py`).
- **`django-money`**: Standardizes currency fields and conversions. Unused in the initial boilerplate version, but available if subscription pricing calculations are needed.
