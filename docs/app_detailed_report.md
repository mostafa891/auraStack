# 🌌 Comprehensive Technical Report & Interface Design — AuraFlow Engine

This report details the architectural enhancements, UI/UX polish, security mappings, and technical structure of **AuraFlow**.

---

## 📂 1. Directory Structure & Architectural Refactoring

The application underwent full architectural refactoring to eliminate redundant legacy HTML templates and ensure 100% SPA compliance:

* **Backend Views**: All security and authentication views in [views_security.py](../apps/users/views_security.py) inherit clean Django `View` controllers rendering Inertia views.
* **Frontend Pages**: Interactive Vue 3 components housed in `frontend/src/pages/Security/` (`PasswordChange.vue`, `MfaList.vue`, `TotpActivate.vue`, etc.).
* **Root Container**: Clean template container in [base.html](../templates/base.html) mounting the root Inertia application.

---

## 🎨 2. UI/UX & Authentication Design

### 2.1 Social Login Layout Positioning
* In [Login.vue](../frontend/src/pages/Auth/Login.vue) and [Register.vue](../frontend/src/pages/Auth/Register.vue): Email and password inputs are placed prominently, followed by a subtle separator ("Or continue with"), and stylish glassmorphic OAuth buttons for Google and GitHub.

### 2.2 Direct OAuth Flow
* Activated `SOCIALACCOUNT_LOGIN_ON_GET = True` and `SOCIALACCOUNT_AUTO_SIGNUP = True` to redirect users directly to Google/GitHub authentication servers without unstyled intermediary confirmation screens, directing first-time signups to [SocialSignup.vue](../frontend/src/pages/Auth/SocialSignup.vue).

### 2.3 Dual Validation & Field Error Mapping
* **Client Validation**: Zod schemas enforce password length, non-numeric checks, and email similarity rules directly in the browser before submission.
* **Server Error Mapping**: Backend password validation errors intercepted by `AllauthAdapter` are mapped directly to the `password` field prop, highlighting errors directly beneath the target input.

---

## 🔒 3. Multi-Tenancy & Workspace Architecture

* **Row-Level Tenant Isolation**: Shared database model using unique workspace slugs, automatic invitation token expiration, and fine-grained Role-Based Access Control (`OWNER`, `ADMIN`, `MEMBER`).
* **Automated Task Queues & Webhooks**: Webhook handlers backed by signature validation and background task execution via Django-Q2.
