# 📦 Module Extraction & Decoupling Guide (AuraStack)

This guide details how developers can extract specific domain modules from **AuraStack** and plug them directly into an existing Django project without taking the entire boilerplate.

---

## 🏗️ Architecture & Domain Isolation

AuraStack applications are isolated inside the `apps/` directory following strict domain separation:

```text
apps/
├── users/         # Auth, Security, 2FA/MFA, Profiles
├── teams/         # Workspaces, Multi-tenancy, RBAC Permissions
├── payments/      # Multi-gateway (Stripe, Paymob, LemonSqueezy, PayPal, Paddle)
└── blog/          # CMS & News publishing
```

---

## 1. Extracting the Multi-Gateway Payment Engine (`apps/payments`)

To plug the payment system into your existing Django app:

### Step 1: Copy Dependencies & Files
Copy `apps/payments/` to your project's `apps/` directory:
```bash
cp -r apps/payments /path/to/your_django_project/apps/
```

### Step 2: Add Dependencies & Settings
Add the following settings to your `settings.py`:
```python
INSTALLED_APPS += [
    "apps.payments",
    "django_q",
]

# Gateway API Keys
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
PAYMOB_API_KEY = os.getenv("PAYMOB_API_KEY", "")
LEMONSQUEEZY_API_KEY = os.getenv("LEMONSQUEEZY_API_KEY", "")
```

### Step 3: Wire API & Webhooks
In your `urls.py`:
```python
from apps.payments.api import private_api, public_api

urlpatterns += [
    path("api/v1/private/", private_api.urls),
    path("api/v1/public/", public_api.urls),
]
```

---

## 2. Extracting Multi-Tenancy & Workspace Isolation (`apps/teams`)

### Step 1: Copy Team Module
```bash
cp -r apps/teams /path/to/your_django_project/apps/
```

### Step 2: Workspace Models & Middleware
Ensure `apps.teams` is added to `INSTALLED_APPS`. To enable auto-sharing of active workspace state with Inertia or REST APIs, include the middleware from `common/middleware.py`:
```python
MIDDLEWARE += [
    "common.middleware.ShareUserDataMiddleware",
]
```

---

## ⚡ Automating Extraction via CLI

AuraStack includes an automated CLI script to bundle any specified module into a zip/tar file:

```bash
# Extract Payments Module
python scripts/cli_extract.py --module payments

# Extract Teams Module
python scripts/cli_extract.py --module teams
```
