# Background Jobs & Hybrid Queue Broker

This document details the asynchronous task queue architecture within AuraStack and how it scales from local development to production.

---

## ⚙️ 1. Hybrid Queue Architecture

AuraStack uses **Django Q2** for background processing. To provide the best developer experience and ensure smooth scaling, we implement a **Hybrid Broker System**:

*   **Local Development (Fallback):** Uses the Django database ORM as the broker. This avoids the need to install Redis locally, keeping dependencies minimal.
*   **Production (Default):** Seamlessly switches to **Redis** if a `REDIS_URL` environment variable is defined, offloading task queue operations entirely from the database.

---

## 🔧 2. Settings Configuration

The configurations are managed in `core/settings/base.py`:

```python
REDIS_URL = env.str("REDIS_URL", default="")

if REDIS_URL:
    # Production-grade Redis broker configuration
    Q_CLUSTER = {
        "name": "auraflow_q",
        "workers": 4,
        "recycle": 500,
        "timeout": 60,
        "redis": REDIS_URL,
    }
else:
    # Local development DB ORM broker configuration
    Q_CLUSTER = {
        "name": "auraflow_q",
        "workers": 2,
        "recycle": 100,
        "timeout": 60,
        "sleep": 1,        # Prevents CPU/read amplification by polling every 1 second
        "save_limit": 0,   # Automatically deletes successful tasks to prevent DB bloat
        "orm": "default",
    }
```

---

## 🏃 3. Running the Worker

To start processing tasks (either from the database ORM or Redis, depending on settings):

```bash
python manage.py qcluster
```

In production, the worker process is automatically run as a separate container/service (managed by the `worker` service in `docker-compose.yml` or your orchestrator).

---

## 📦 4. Queuing a Task

Tasks are scheduled asynchronously using `async_task`:

```python
from django_q.tasks import async_task

# Offloads task signature verification and database updates to the background
async_task("apps.payments.tasks.process_stripe_webhook", payload, signature)
```

*   **Failed Tasks:** Retained in the database for inspection, troubleshooting, and retry workflows in the Django Admin.
*   **Successful Tasks:** Cleaned up automatically (`save_limit: 0`) in ORM mode to preserve database health and storage limits.
