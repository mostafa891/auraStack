# 🌌 auraStack SaaS Boilerplate & Internal Tools Engine

Production-grade, modular Full-Stack SaaS Boilerplate & Internal Platform Engine engineered with modern 2026 web architecture.

[![CI/CD Pipeline](https://github.com/mostafa891/auraStack/actions/workflows/ci.yml/badge.svg)](#)
![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)
![Django](https://img.shields.io/badge/Django-5.1-092E20?style=for-the-badge&logo=django)
![Vue.js](https://img.shields.io/badge/Vue.js-3.5-4FC08D?style=for-the-badge&logo=vuedotjs)
![Inertia.js](https://img.shields.io/badge/Inertia.js-v2-9553E9?style=for-the-badge&logo=inertia)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-v4-06B6D4?style=for-the-badge&logo=tailwindcss)
![TypeScript](https://img.shields.io/badge/TypeScript-6.0-3178C6?style=for-the-badge&logo=typescript)

---

## 💡 Why auraStack? (Time & Effort Savings)

> **Launch your SaaS or internal platform in days—saving 200+ hours of setup time, engineering effort, and configuration headaches.**

Building modern SaaS infrastructure from scratch burns weeks of development time on tedious, repetitive setup: authentication, 2FA, workspace isolation, payment gateways, background workers, and E2E test suites. **auraStack** gives you this entire production-grade foundation out of the box so you can focus 100% on your core product logic.

### ⏱️ Time & Engineering Effort Savings

| Component / Feature | Building from Scratch | With auraStack | Time & Effort Saved |
| :--- | :--- | :--- | :--- |
| **B2B Multi-Tenancy & RBAC** | 35 – 50 Hours | 0 Hours (Pre-built) | 4–6 Days of complex security coding |
| **SOC2-Grade Auth, OAuth & 2FA/TOTP** | 30 – 45 Hours | 0 Hours (Pre-built) | 4–5 Days of identity & session setup |
| **5 Payment Gateways (inc. Paymob MENA)** | 40 – 60 Hours | 0 Hours (Pre-built) | 5–7 Days of API & webhook integration |
| **Zero REST API Boilerplate (Inertia v2)** | 25 – 35 Hours | 0 Hours (Pre-built) | 3–4 Days of state & fetcher duplication |
| **70+ Automated Pytest & Playwright Tests** | 40 – 50 Hours | 0 Hours (Pre-built) | 4–6 Days of QA script writing |
| **Dark-Mode Admin & Task Queues** | 20 – 30 Hours | 0 Hours (Pre-built) | 2–3 Days of dashboard configuration |
| **TOTAL EFFORT SAVED** | **190 – 270 Hours** | **Instant Setup** | **4–6 Weeks of Full-Time Engineering Saved** |

👉 **Read the full developer focus & architectural breakdown in [Why auraStack? (docs/WHY_AURASTACK.md)](docs/WHY_AURASTACK.md).**

---

## 🛠️ Core Technology Stack

auraStack leverages a modern hybrid architecture combining robust backend security with rich, dynamic Single Page Application (SPA) reactive user experiences:

* **Backend Engine:** [Django 5](https://www.djangoproject.com/) (LTS release).
* **Frontend SPA:** [Vue 3](https://vuejs.org/) (Composition API with `<script setup lang="ts">`) powered by [Vite](https://vitejs.dev/).
* **Protocol Bridge:** [Inertia.js v2](https://inertiajs.com/) (Direct server-driven SPA routing without full-page reloads or unnecessary REST API boilerplate).
* **Design & Styling:** [Tailwind CSS v4](https://tailwindcss.com/) (CSS-first configuration with dynamic dark mode design tokens).
* **Identity & Security:** [django-allauth](https://django-allauth.readthedocs.io/) (Custom adapters, username-less email authentication, TOTP/MFA, and OAuth2 connections).
* **Payment Gateways:** 5 pre-wired providers (Stripe, LemonSqueezy, PayPal, Paddle, and Paymob MENA).
* **Admin Dashboard:** [django-unfold](https://github.com/unfoldadmin/django-unfold) (Sleek dark-mode-first administration panel).
* **Task Queues & Webhooks:** Django-Q2 background worker clusters and signature-verified webhook handlers.

---

## ⚡ Developer Automation & DX (`Makefile`)

The repository includes a `Makefile` for instant one-word developer commands:

```bash
make dev      # Starts Django backend & Vite dev servers concurrently
make test     # Runs Pytest unit and browser E2E test suite
make verify   # Runs full system verification (tests + dry-run migrations)
make lint     # Runs Ruff linter checks across Python codebase
make migrate  # Applies pending Django database migrations
```

---

## 📂 Project Architecture & Directory Structure

Organized following domain-driven, modular application standards:

```text
aurastack/
│
├── .github/workflows/       # Automated CI/CD GitHub Actions pipeline
├── apps/                    # Domain-driven modular local applications
│   ├── users/               # Custom User model, security views, MFA, avatar management
│   ├── teams/               # Multi-tenancy workspaces, RBAC, member invitations
│   ├── payments/            # 5 payment gateways, webhooks, subscription tracking
│   └── blog/                # Content and internal publishing management
│
├── common/                  # Shared cross-cutting concerns & utilities
│   ├── middleware.py        # Inertia global shared state (auth, active workspace)
│   ├── logger.py            # Audit logging & security tracking
│   ├── results.py           # Standardized ServiceResult response container
│   └── utils/               # General normalization and helper functions
│
├── core/                    # Core settings, WSGI/ASGI gateways, & root URLs
│   ├── settings/            # Modular settings (base, local, production)
│   ├── urls.py              # Root routing table & global security view overrides
│   └── wsgi.py / asgi.py    # Production gateway entry points
│
├── frontend/                # Complete SPA frontend (Vue 3 + TypeScript + Vite)
│   ├── src/
│   │   ├── pages/           # Inertia page views (Auth, Profile, Workspaces, Landing)
│   │   ├── layouts/         # Shared wrappers & Toast notification containers
│   │   ├── composables/     # Vue hooks (i18n, Zod schema adapter)
│   │   └── main.ts          # Application entry point & Inertia initialization
│   └── vite.config.ts       # Vite build setup synced with django-vite
│
├── render.yaml              # 1-Click Render.com deployment configuration
├── fly.toml                 # 1-Click Fly.io deployment configuration
├── Makefile                 # Developer automation shortcuts
├── pytest.ini               # Pytest suite configuration
├── requirements.txt         # Python dependencies specification
└── ruff.toml                # Code quality & linter configuration
```

---

## 🩺 System Health Monitoring Endpoint

auraStack exposes a lightweight system health probe at `/api/v1/public/health` for container orchestration and status monitoring:

```json
GET /api/v1/public/health

Response 200 OK:
{
  "status": "healthy",
  "database": "ok",
  "service": "auraStack",
  "version": "1.0.0"
}
```

---

## 🔒 Security & Identity Architecture

Full integration with `django-allauth` wrapped entirely within Inertia Vue 3 views:

1. **Multi-Factor Authentication (MFA/2FA):** TOTP authentication via Google Authenticator with active QR code generation and recovery codes (`/auth/mfa/`).
2. **Username-less Auth:** Clean `email` primary key login with server-side Django password complexity validators.
3. **Avatar Security:** Direct magic-bytes header verification (PNG/JPEG/WEBP) before saving to disk, plus a **Remove Avatar** action.
4. **Password Recovery & Password Change:** Automated password reset links and authenticated password change flows.
5. **OAuth Social Connections:** One-click Google and GitHub social logins.

---

## 🚀 Setup & Local Execution Guide

### 1. Environment & Dependencies Installation
```bash
# Create Python virtual environment
python -m venv .venv

# Activate environment (Windows)
.venv\Scripts\activate

# Activate environment (Linux / macOS)
source .venv/bin/activate

# Install Python requirements
pip install -r requirements.txt

# Install Playwright browser drivers for E2E testing
playwright install
```

### 2. Database Migration & Seed Data
```bash
# Run database migrations
python manage.py migrate

# Seed instant test accounts
python manage.py runscript seed_data
```

### 3. Running Development Servers
```bash
make dev
# Or manually:
python manage.py runserver
npm run dev
```

---

## 🚀 1-Click Cloud Deployment

### Render.com
auraStack includes a pre-configured `render.yaml` specification for Render.com deployment.

### Fly.io
Deploy to Fly.io using the included `fly.toml`:
```bash
fly launch
fly deploy
```

---

## 🧪 QA & Testing Strategy

### 1. Automated Quality Gates (Ruff)
```bash
make lint
```

### 2. Pytest & Playwright E2E Suite
```bash
make test
```
* **Backend Tests:** Verifies custom user model, tenant isolation, workspace lockout, N+1 query limits, and webhook security.
* **E2E Playwright Tests:** Launches real Chromium instances to execute end-to-end user journeys.

---

## 📚 Technical Reference Documentation

Detailed architectural and technical guides are available in the `docs/` directory:

1. **[Django Core Guide](docs/reference/django_core.md)**
2. **[Django Allauth Integration](docs/reference/django_allauth.md)**
3. **[Inertia-Django Architecture](docs/reference/inertia_django.md)**
4. **[Multi-Tenancy & Teams Guide](docs/reference/django_multi_tenancy.md)**
5. **[Pytest & Playwright Guide](docs/reference/pytest_playwright.md)**
