# Production Deployment & Containerization

This document outlines the deployment strategy, Docker production architecture, background workers orchestration, and storage setups for AuraStack.

---

## 🐋 1. Docker Production Architecture

In production, the application is split into two primary container services: the **Web Application Server** and the **Q2 Background Worker Server**. Both run from the same multi-stage Docker image but execute different commands.

### docker-compose.yml Services:
*   **`web`:** Runs the WSGI server (Gunicorn) to serve client requests.
*   **`worker`:** Runs the background task cluster (`python manage.py qcluster`) to process payment webhooks, async emails, and limits checks.
*   **`db`:** PostgreSQL 16 Alpine container with auto-initialized health checks.

---

## 🚀 2. Production Web Server (Gunicorn & Whitenoise)

*   **WSGI Web Server:** Gunicorn manages Python worker processes concurrently.
*   **Static Asset Serving:** Whitenoise caches, compresses, and serves static frontend assets directly from the python container, eliminating the need for Nginx.

*Production run command (run by the `web` container):*
```bash
gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

---

## 📦 3. Media Storage (S3 / Cloudflare R2)

Standard container storage is ephemeral (any uploaded file like user avatars is deleted when a container restarts). 

To persist uploads, set `USE_S3_STORAGE=True` and configure your credentials. The application will automatically stream all uploads (via `django-storages[boto3]`) to AWS S3, Cloudflare R2, or Backblaze B2.

---

## 🔒 4. Production Checklist

Ensure the following environment variables are injected into your hosting container environment:
*   `DEBUG=False`
*   `DJANGO_SETTINGS_MODULE=core.settings.production`
*   `SECURE_SSL_REDIRECT=True`
*   `DATABASE_URL=postgres://user:pass@host:port/dbname`
*   `REDIS_URL=redis://user:pass@host:port` (Switches queue broker to high-performance Redis)
*   `USE_S3_STORAGE=True`
*   `EMAIL_BACKEND=anymail.backends.resend.EmailBackend` (or SMTP)
