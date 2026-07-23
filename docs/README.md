# AuraStack Documentation Index

Welcome to the **AuraStack SaaS Engine** documentation. This directory contains detailed specifications, architecture designs, and development workflows for the boilerplate.

---

## 📂 Documentation Structure

### 1. [Developer Onboarding & Contributing](contributing/index.md)
*   **Quickstart Guide:** Run the engine locally in 3 steps.
*   **Code Standards:** Ruff configuration, formatting, and pre-commit hooks.

### 2. [Architecture](architecture/database.md)
*   **[Database Architecture](architecture/database.md):** UUID primary keys, Soft Delete logic, database indexes, and transactions.
*   **[Configuration](architecture/configuration.md):** Settings split (dev, test, production) and environment variable management.
*   **[Error Handling](architecture/errors.md):** Uniform API validation response structures, standard exceptions, and logging.
*   **[Django Ninja API](architecture/api-ninja.md):** Type-safe endpoints, public/private routing, and Pydantic validation.

### 3. [Authentication & Security](authentication/index.md)
*   **Session & OAuth:** Session authentication and Google/GitHub OAuth setup.
*   **Two-Factor Authentication (2FA):** TOTP (Google Authenticator) verification and recovery codes.
*   **Security Headers:** CSRF split design, HSTS, and CSP middleware.

### 4. [Multi-Tenancy & Isolation](multi-tenancy/index.md)
*   **Workspace Model:** Multi-tenant separation logic.
*   **Membership & Roles:** Workspace roles (`OWNER`, `ADMIN`, `MEMBER`) and permissions checking.

### 5. [Billing & Subscriptions](billing/index.md)
*   **Gateway Integrations:** Stripe and Paymob checkout flows.
*   **Webhooks:** Asynchronous webhook validation and replay-attack protection.
*   **Restricted Mode:** Workspace lock-state when plan limits are exceeded.

### 6. [Background Jobs](background-jobs/index.md)
*   **Django Q2:** Background task queues using the database ORM as the broker.

### 7. [Testing](testing/index.md)
*   **Pytest:** Standard unit and integration test runs.
*   **Playwright E2E:** Native browser simulation tests (e.g., verifying 2FA, avatar upload).

### 8. [Deployment](deployment/index.md)
*   **Docker Production:** Gunicorn, Whitenoise, and isolated docker containers.
