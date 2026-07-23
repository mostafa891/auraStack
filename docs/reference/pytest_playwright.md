# 🧪 Pytest & Playwright Reference Guide

This document describes the automated testing architecture of **AuraFlow**, including unit testing, integration tests, and End-to-End (E2E) browser verification.

---

## ⚙️ Test Environments Configuration

The test suite is powered by `pytest` and runs on the development database.

### `pytest.ini`
Configures the test runner to use development settings and cache schema builds:
```ini
[pytest]
DJANGO_SETTINGS_MODULE = core.settings.local
python_files = tests.py test_*.py *_tests.py
addopts = --reuse-db
```

### Shared Fixtures (`conftest.py`)
Located in [conftest.py](../../apps/users/tests/conftest.py), this file defines common elements and global test environment settings:
- **Async Safety**: `os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"` enables querying the Django ORM inside async testing contexts.
- **`client`**: Standard Django mock request client.
- **`test_user`**: Populates the test database with a user preconfigured with preferences.

---

## 📂 Test Suites

Tests are separated into distinct modules based on functionality.

### 1. Model Verification (`test_models.py`)
Verifies user database constraints, password encryption, and superuser privilege settings.

### 2. Service Verification (`test_services.py`)
Tests `AuthService` registration logic, duplicate email rejection, and audit trails logging.

### 3. View Routing & Protection (`test_views.py`)
Verifies page status codes, checks redirects for unauthenticated users, and tests profile updates.

### 4. Browser Integration testing (`test_auth_flow.py`)
Located in [test_auth_flow.py](../../tests/e2e/test_auth_flow.py), this E2E test runs Chromium using **Playwright** to test full user sessions:
1. **Sign-up Flow**: Enters user credentials and confirms password matching on `/auth/register/`.
2. **Redirect Validation**: Asserts that registration redirects the browser to the `/profile/` dashboard.
3. **Theme Visual test**: Modifies the theme setting to `DARK`, submits the form, and asserts that the root document DOM class list dynamically updates:
   ```typescript
   page.evaluate("() => document.documentElement.classList.contains('dark')")
   ```
4. **Logout Flow**: Clicks the logout button and asserts the user is securely returned to `/auth/login/`.
