# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- **Paymob** full API integration (Egyptian & MENA market) — 3-step checkout flow with HMAC-SHA512 webhook verification
- **LemonSqueezy** full API integration — Checkout sessions, subscription management, HMAC-SHA256 webhooks
- **Paddle Billing** (v2) integration — Customer management, transaction checkout, webhook verification
- **PayPal Subscriptions** API integration — OAuth2 flow, subscription creation, webhook verification
- **Webhook handlers** for all payment providers: LemonSqueezy, Paddle, PayPal
- **Plan limit enforcement** — `invite_member` now checks `max_members` from the active subscription plan
- `payments/selectors.py` — `get_workspace_plan()` and `get_plan_limit()` helper functions
- **Blog: Tag model** — Categorize posts with tags (ManyToMany)
- **Blog: Author field** — Link posts to registered users
- **Blog: Cover image** — Upload per-post cover images
- **Blog: Reading time** — Auto-calculated property (200 words/min)
- **Blog: Pagination** — 10 posts per page with tag filtering
- **Blog: Index redesign** — Premium 3-column grid with cover images, tags, reading time, author
- **Blog: Detail redesign** — Full article view with meta bar, avatar, share button
- `CHANGELOG.md` — This file
- Redis warning in production if `REDIS_URL` is not set
- `SITE_URL`, `REDIS_URL`, and all payment gateway keys documented in `.env.example`

### Fixed
- `plan_id` was hardcoded to `"pro"` in Stripe webhook handler — now reads from `checkout.session.metadata.plan_id`
- `FORMS_URLFIELD_ASSUME_HTTPS` deprecated setting removed (caused 17 warnings per test run)
- `DEFAULT_FROM_EMAIL` default changed from `webmaster@localhost` to `noreply@yourdomain.com`
- `Paymob`, `LemonSqueezy`, `Paddle`, `PayPal` were returning stub/fake responses — all replaced with real API implementations
- `process_paymob_webhook` was a no-op `pass` — now processes real Paymob payment notifications

---

## [1.0.0] — 2026-07-13

### Added
- Django 5.2 + Vue 3 + Inertia.js full-stack SaaS boilerplate
- django-allauth integration: email auth, 2FA/MFA (TOTP + WebAuthn), social login (Google + GitHub)
- Multi-tenant workspace system (OWNER / ADMIN / MEMBER roles)
- Workspace invitations via email
- Soft delete for workspaces with restore capability
- Stripe Checkout + Customer Portal + Webhook handler
- django-unfold admin panel (dark mode)
- Sentry SDK integration for error tracking
- WhiteNoise for static file serving in production
- S3 / Cloudflare R2 support for media storage
- django-q2 for background tasks (Redis or ORM broker)
- Anymail / Resend email integration
- django-ratelimit on authentication endpoints
- django-querycount + nplusone for N+1 detection in development
- Multi-stage Dockerfile (Node build → Python runtime, non-root user)
- docker-compose with PostgreSQL + Healthcheck
- pytest + Playwright E2E tests (62 tests passing)
- Tenant isolation tests (BOLA/IDOR protection)
- Webhook security tests
- Rate limiting tests
- Soft delete tests
- CLAUDE.md and TECHNICAL_DOC.md for onboarding
