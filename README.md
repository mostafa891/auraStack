# 🌌 auraStack

Production-ready Django + Vue + Inertia SaaS Boilerplate.

Build multi-tenant SaaS applications **without writing REST serializer boilerplate** — featuring authentication, RBAC, 5 payment gateways, Docker, CI/CD, and automated testing out-of-the-box.

[![CI/CD Pipeline](https://github.com/mostafa891/auraStack/actions/workflows/ci.yml/badge.svg)](#)
![Python](https://img.shields.io/badge/Python-3.12%2B-blue?style=for-the-badge&logo=python)
![Django](https://img.shields.io/badge/Django-5.1-092E20?style=for-the-badge&logo=django)
![Vue.js](https://img.shields.io/badge/Vue.js-3.5-4FC08D?style=for-the-badge&logo=vuedotjs)
![Inertia.js](https://img.shields.io/badge/Inertia.js-v2-9553E9?style=for-the-badge&logo=inertia)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-v4-06B6D4?style=for-the-badge&logo=tailwindcss)
![TypeScript](https://img.shields.io/badge/TypeScript-6.0-3178C6?style=for-the-badge&logo=typescript)

---

## ⚡ Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/mostafa891/auraStack.git
cd auraStack

# 2. Setup environment & dependencies
cp .env.example .env
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. Migrate & seed initial test data
python manage.py migrate
python manage.py runscript seed_data

# 4. Start backend & frontend dev servers concurrently
make dev
```

Visit `http://localhost:8000` to see your application running.

---

## 🖼️ Preview & UI Screenshots

<!-- TODO: Add demo GIF or screenshots here -->
> **User Interface Preview:** Includes dark/light mode SPA pages for Authentication, Workspace Governance, MFA Security, and Billing Settings.

| Landing Page | Workspaces & Team RBAC |
| :---: | :---: |
| *(Landing Page Preview)* | *(Workspace Governance)* |

| Identity & MFA Security | Billing & Subscriptions |
| :---: | :---: |
| *(TOTP / 2FA Settings)* | *(Multi-Gateway Checkout)* |

---

## ✨ Key Features

- ✅ **B2B Multi-Tenancy:** Isolated team workspaces, member invitations, and granular RBAC roles (`OWNER`, `ADMIN`, `MEMBER`).
- ✅ **Complete Authentication:** Username-less email login, password recovery, TOTP 2FA/MFA, and Google/GitHub social OAuth.
- ✅ **5 Pre-Integrated Payment Gateways:** Stripe, PayPal, LemonSqueezy, Paddle, and **Paymob (MENA)** out-of-the-box.
- ✅ **Zero REST API Boilerplate:** Powered by Inertia.js v2 — Django routes directly render Vue 3 SPA components.
- ✅ **Dark Mode & Styling:** Built with Tailwind CSS v4 and `django-unfold` admin dashboard.
- ✅ **Background Queues & Webhooks:** Django-Q2 worker queues with signature-verified webhook security handlers.
- ✅ **Enterprise Security & Compliance:** Soft-deletes, rate limiting, security headers, and binary avatar verification.
- ✅ **Automated QA Suite:** 72 automated backend Pytest tests + Playwright E2E browser automation suite.
- ✅ **Cloud Deployment Ready:** Pre-configured for Render.com, Fly.io, and Docker containerization.

---

## 🛠️ Core Technology Stack

* **Backend Engine:** [Django 5](https://www.djangoproject.com/)
* **Frontend SPA:** [Vue 3](https://vuejs.org/) (Composition API + `<script setup lang="ts">`) powered by [Vite](https://vitejs.dev/)
* **Protocol Bridge:** [Inertia.js v2](https://inertiajs.com/) (Server-driven SPA routing)
* **Styling & Tokens:** [Tailwind CSS v4](https://tailwindcss.com/)
* **Admin Interface:** [django-unfold](https://github.com/unfoldadmin/django-unfold)
* **Task Queue:** [Django-Q2](https://github.com/django-q2/django-q2)
* **Testing:** [Pytest](https://docs.pytest.org/) & [Playwright E2E](https://playwright.dev/python/)

---

## ⚡ Developer DX (`Makefile`)

auraStack includes simple automation commands:

```bash
make dev      # Starts Django backend & Vite dev servers concurrently
make test     # Runs Pytest unit, integration, and browser E2E tests
make verify   # Full system check (tests + dry-run migrations)
make lint     # Runs Ruff linter across the Python codebase
make migrate  # Applies pending Django database migrations
```

---

## 📂 Project Architecture

Organized using domain-driven modular standards:

```text
aurastack/
│
├── .github/workflows/       # Automated CI/CD GitHub Actions pipeline
├── apps/                    # Domain-driven local applications
│   ├── users/               # Custom User model, MFA security, avatar management
│   ├── teams/               # Workspaces, RBAC, member invitations
│   ├── payments/            # 5 payment gateways, webhooks, plan subscriptions
│   └── blog/                # Markdown content publishing
│
├── common/                  # Shared middleware, audit logger, ServiceResult containers
├── core/                    # Modular settings (base, local, production), URLs, WSGI/ASGI
├── frontend/                # Vue 3 + TypeScript SPA (pages, layouts, composables)
├── render.yaml              # Render.com 1-click deployment
├── fly.toml                 # Fly.io 1-click deployment
├── Makefile                 # Developer CLI shortcuts
└── pytest.ini               # Test suite configuration
```

---

## 🧪 Testing & Quality Assurance

Run the automated test suite locally:

```bash
# Run unit, integration, and Playwright E2E tests
make test
```

- **Backend Unit Tests:** Verifies tenant isolation, N+1 query limits, workspace lockout states, and webhook security.
- **E2E Playwright Tests:** Runs headless Chromium browser simulation testing registration, 2FA verification, and team invitation flows.

---

## 📚 Technical Documentation & Guides

For detailed architectural specifications, check out the `docs/` folder:

1. **[Why auraStack? (Value & Velocity Breakdown)](docs/WHY_AURASTACK.md)**
2. **[Architecture & Database Guide](docs/architecture/database.md)**
3. **[Authentication & Security Guide](docs/authentication/index.md)**
4. **[Multi-Tenancy & Workspace RBAC](docs/multi-tenancy/index.md)**
5. **[Billing & Gateways Reference](docs/billing/index.md)**
6. **[Testing Strategy Guide](docs/testing/index.md)**
7. **[Production Deployment Guide](docs/deployment/index.md)**
