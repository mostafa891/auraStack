# 🔐 Django Allauth Integration Guide

This document describes how **django-allauth** is configured, extended, and integrated into the **AuraFlow** SPA architecture.

---

## ⚙️ Core Configuration Settings

AuraFlow leverages django-allauth for authentication, MFA, and social logins. Key overrides in [base.py](../../core/settings/base.py) include:

```python
# Authentication Method
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_LOGIN_METHODS = {"email"}

# Policies
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory" # "none" in local development
```

---

## 🛠️ Adapter Layer: `AllauthAdapter`

To decouple the Django views from allauth's internal APIs, AuraFlow implements a service adapter in [allauth.py](../../apps/users/adapters/allauth.py).

### Authentication
`AllauthAdapter.authenticate_user(request, email, password) -> ServiceResult`
- Instantiates allauth's `LoginForm` programmatically with request context.
- Returns a normalized `ServiceResult` object encapsulating success status, error messages, and structured codes.

### Registration
`AllauthAdapter.register_user(request, email, password) -> ServiceResult`
- Calls allauth's `adapter.new_user()` and saves the user password securely.
- Catches `ValidationError` and maps it to standard form validation errors.
- Catches database `IntegrityError` to resolve potential registration race conditions directly from the database engine.
- Triggers allauth's standard registration lifecycle processes (signals, email verifications) via `complete_signup`.

---

## 🔄 SPA Integration (HTML to Vue/Inertia Views)

Rather than rendering default django-allauth Django Templates (which cause full-page reloads and break SPA states), AuraFlow wraps allauth generic views in custom Inertia views located in [views_security.py](../../apps/users/views_security.py).

### Custom Security Views
1. **Password Change**: `PasswordChangeView` wrapping allauth's password change form logic.
2. **MFA Settings List**: `MfaListView` checking active authenticators and passing them as props.
3. **MFA Authenticate**: `MfaAuthenticateView` used during multi-factor logins.
4. **TOTP Activation**: `TotpActivateView` rendering the TOTP SVG QR Code and Secret Key as props.
5. **TOTP Deactivation**: `TotpDeactivateView` verifying the account password to disable TOTP.
6. **Social Connections**: `SocialConnectionsView` listing linked OAuth providers.

### 🛡️ Dual Password Validation & Field Error Mapping
To provide a smooth user experience alongside solid backend protection, AuraFlow applies a dual password validation layer:
* **Client-Side (Zod & VeeValidate)**: Enforces minimum 8 characters, non-numeric checks, and prevents using passwords similar to the email prefix directly in the browser before the form is sent.
* **Server-Side (Django Password Validators)**: Performs full checks (similarity, length, common passwords, numeric). Any caught `ValidationError` is intercepted by [AllauthAdapter](../../apps/users/adapters/allauth.py) and mapped directly to the `"password"` key in the error dictionary, ensuring the error is displayed directly under the password input in Vue instead of as a generic page alert.

### Global URL Overrides
In [core/urls.py](../../core/urls.py), the custom Inertia security views are registered globally before allauth's URL patterns. This ensures that any internal redirect within allauth (e.g. redirecting to MFA verification after login) resolves to the Inertia page instead of the old HTML templates.
