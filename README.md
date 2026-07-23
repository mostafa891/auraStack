# 🌌 AuraFlow SaaS Boilerplate & Internal Tools Engine

Production-grade, modular Full-Stack SaaS Boilerplate & Internal Platform Engine engineered with modern 2026 web architecture.

![Python](https://img.shields.io/badge/Python-3.13-blue?style=for-the-badge&logo=python)
![Django](https://img.shields.io/badge/Django-5.1-092E20?style=for-the-badge&logo=django)
![Vue.js](https://img.shields.io/badge/Vue.js-3.5-4FC08D?style=for-the-badge&logo=vuedotjs)
![Inertia.js](https://img.shields.io/badge/Inertia.js-0.6-9553E9?style=for-the-badge&logo=inertia)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-v4-06B6D4?style=for-the-badge&logo=tailwindcss)
![TypeScript](https://img.shields.io/badge/TypeScript-6.0-3178C6?style=for-the-badge&logo=typescript)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub_Actions-2088FF?style=for-the-badge&logo=githubactions)

---

## 🛠️ Core Technology Stack

AuraFlow leverages a modern hybrid architecture combining robust backend security with rich, dynamic Single Page Application (SPA) reactive user experiences:

* **Backend Engine:** [Django 5](https://www.djangoproject.com/) (LTS release).
* **Frontend SPA:** [Vue 3](https://vuejs.org/) (Composition API with `<script setup lang="ts">`) powered by [Vite](https://vitejs.dev/).
* **Protocol Bridge:** [Inertia.js](https://inertiajs.com/) (Direct server-driven SPA routing without full-page reloads or unnecessary REST API boilerplate).
* **Design & Styling:** [Tailwind CSS v4](https://tailwindcss.com/) (CSS-first configuration with dynamic dark mode design tokens).
* **Identity & Security:** [django-allauth](https://django-allauth.readthedocs.io/) (Custom adapters, username-less email authentication, TOTP/MFA, and OAuth2 connections).
* **Admin Dashboard:** [django-unfold](https://github.com/unfoldadmin/django-unfold) (Sleek dark-mode-first administration panel).
* **Task Queues & Webhooks:** Django-Q2 background worker clusters and signature-verified webhook handlers.

---

## 📂 Project Architecture & Directory Structure

Organized following domain-driven, modular application standards:

```text
auraflow/
│
├── apps/                    # Domain-driven modular local applications
│   ├── users/               # Custom User model, security views, MFA, adapters
│   ├── teams/               # Multi-tenancy workspaces, RBAC, member invitations
│   ├── payments/            # Gateway webhooks, plan limits, subscription tracking
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
│   │   ├── pages/           # Inertia page views (Auth, Security, Workspaces)
│   │   ├── layouts/         # Shared wrappers & Toast notification containers
│   │   ├── composables/     # Vue hooks (Form error parser, Zod schema adapter)
│   │   ├── types/           # TypeScript interface definitions
│   │   └── main.ts          # Application entry point & Inertia initialization
│   └── vite.config.ts       # Vite build setup synced with django-vite
│
├── scripts/                 # Automation & seed data generation scripts
│   └── seed_data.py         # Instant demo account population script
│
├── pytest.ini               # Pytest suite configuration
├── requirements.txt         # Python dependencies specification
├── ruff.toml                # Code quality & linter configuration
└── .pre-commit-config.yaml  # Pre-commit quality gates
```

---

## 🔒 Security & Identity Architecture

Full integration with `django-allauth` wrapped entirely within Inertia Vue 3 views:

1. **Multi-Factor Authentication (MFA/2FA):** TOTP authentication via Google Authenticator with active QR code generation and recovery codes (`/accounts/mfa/list/`).
2. **Username-less Auth:** Clean `email` primary key login with server-side Django password complexity validators mapped directly to Vue field inputs.
3. **Password Recovery & Password Change:** Automated password reset links and authenticated password change flows.
4. **OAuth Social Connections:** One-click Google and GitHub social logins with glassmorphic signup onboarding.

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
> **Pre-populated Demo Accounts:**
> *   **Superadmin User:** `admin@auraflow.com` | Password: `AdminPass123!`
> *   **Standard User:** `user@auraflow.com` | Password: `UserPass123!`

### 3. Running Development Servers
To run locally, execute the backend and frontend development servers concurrently:

```bash
# Terminal 1: Run Django Backend Server
python manage.py runserver

# Terminal 2: Run Vite Frontend Dev Server
npm run dev
```

---

## 🐳 Docker Production Setup

Run the entire stack (Gunicorn + Vite production bundle + PostgreSQL + Django-Q Worker) in isolated non-root containers:

```bash
# Build and run containers
docker-compose up --build
```
* Multi-stage build (`Node 20 Alpine` builds frontend assets, `Python 3.13 Slim` executes Gunicorn).
* Non-privileged security user (`appuser`, UID 10000) for OWASP compliance.
* Built-in container healthchecks.

---

## 🧪 QA & Testing Strategy

### 1. Automated Quality Gates (Ruff)
```bash
# Run Linter & Formatter checks
ruff check --fix
ruff format
```

### 2. Pytest & Playwright E2E Suite
```bash
# Run complete test suite
pytest
```
* **Backend Tests:** Verifies custom user model, tenant isolation, workspace lockout, N+1 query limits, and webhook security.
* **E2E Playwright Tests:** Launches real Chromium instances to execute end-to-end user journeys (Registration, Login, MFA verification, workspace role management, and dynamic Dark/Light theme switching).

---

## 📚 Technical Reference Documentation

Detailed architectural and technical guides are available in the `docs/` directory:

1. **[Django Core Guide](docs/reference/django_core.md):** Base configurations, custom user model, lifecycle middleware.
2. **[Django Allauth Integration](docs/reference/django_allauth.md):** Authentication adapters, MFA, dual password validation.
3. **[Inertia-Django Architecture](docs/reference/inertia_django.md):** Page rendering, shared state props, views setup.
4. **[Django Vite Integration](docs/reference/django_vite.md):** HMR setup, production asset manifest parsing.
5. **[Django Unfold Admin](docs/reference/django_unfold.md):** Modern administrative panel customization.
6. **[Vue 3 Composition API Guide](docs/reference/vue3.md):** SFC structures, Zod v4 validation adapter, toast store.
7. **[Tailwind CSS v4 Guide](docs/reference/tailwind_v4.md):** CSS-first design tokens, dynamic dark mode switching.
8. **[Pytest & Playwright Guide](docs/reference/pytest_playwright.md):** Backend unit tests, async fixtures, E2E browser testing.
9. **[Django Helper Packages](docs/reference/django_packages.md):** Environ, lifecycle, storages, cleanup.
10. **[Multi-Tenancy & Teams Guide](docs/reference/django_multi_tenancy.md):** Workspaces, RBAC permissions, invitation flows.
