# Configuration & Environments

This document details the configuration system of AuraStack, explaining how settings are split, environment secrets are managed, and production integrations are configured.

---

## ⚙️ 1. Settings Split

Django configurations are split into modular files under `core/settings/` to separate local development setups from production requirements and automated test pipelines:

```
core/settings/
├── __init__.py
├── base.py          # Shared base settings (Apps, Middleware, Hybrid Q_CLUSTER)
├── local.py         # Local development overrides (DEBUG=True, SQLite, Console Mail)
├── production.py    # Production hardened settings (Sentry, S3/R2 Storages, SMTP/Anymail, PostgreSQL)
└── test.py          # Fast unit testing configurations (In-memory databases)
```

---

## 🔑 2. Environment Variables Checklist (.env)

We use `django-environ` to load configurations from a local `.env` file. Refer to `.env.example` in the workspace root for a clean blueprint.

### A. General & Security Settings
*   `DEBUG`: `True` for development, `False` in production.
*   `SECRET_KEY`: A cryptographically secure random string.
*   `ALLOWED_HOSTS`: List of domains allowed to request Django (e.g. `yourdomain.com`).
*   `SITE_URL`: Root canonical URL of your website (e.g. `https://yourdomain.com`).

### B. Database & Redis (Queues)
*   `DATABASE_URL`: Connection string pointing to your PostgreSQL (Production) or local SQLite.
*   `REDIS_URL`: If defined, switches the Q2 background worker from ORM to Redis.

### C. Email Configurations
*   `EMAIL_BACKEND`:
    *   `django.core.mail.backends.console.EmailBackend` (Default local)
    *   `anymail.backends.resend.EmailBackend` (Resend API in production)
    *   `django.core.mail.backends.smtp.EmailBackend` (Standard SMTP in production)
*   `RESEND_API_KEY`: API key required if using Resend backend.
*   `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`: Credentials for SMTP.
*   `DEFAULT_FROM_EMAIL`: Sender address for all automated transactional emails.

### D. Cloud Storage (AWS S3 / Cloudflare R2)
*   `USE_S3_STORAGE`: Set to `True` in production to upload media assets (avatars, uploads) to S3/R2 instead of local files.
*   `AWS_ACCESS_KEY_ID`: Cloud storage access key.
*   `AWS_SECRET_ACCESS_KEY`: Cloud storage secret key.
*   `AWS_STORAGE_BUCKET_NAME`: Bucket name.
*   `AWS_S3_ENDPOINT_URL`: Custom endpoint URL (e.g., `https://<accountid>.r2.cloudflarestorage.com` if using Cloudflare R2).

### E. Error Tracking
*   `SENTRY_DSN`: Sentry DSN key to enable error reporting in production.

---

## 🔒 3. Secret Rotation & Production Security

For production builds (e.g. Docker Compose), secrets are passed dynamically via environment injections or mounting Docker Secrets. 

*   **Key Rotation:** Standard key rotations (like renewing the `SECRET_KEY`) can be performed without code downtime by injecting the new key and updating running container environments.
