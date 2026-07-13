# Authentication & Security

This document covers the user authentication layer, multi-factor authentication (MFA), and browser security configurations in AuraStack.

---

## 🍪 1. Session Authentication & CSRF
AuraStack uses standard Django session cookies for authentication, providing a secure, server-controlled session state.

*   **CSRF Protection:** Every state-mutating API call from the Inertia frontend must send the `X-CSRFToken` header.
*   **Cookie Flags:** In production, session and CSRF cookies are hardened:
    *   `SESSION_COOKIE_SECURE = True`
    *   `SESSION_COOKIE_HTTPONLY = True`
    *   `SESSION_COOKIE_SAMESITE = 'Lax'`

---

## 🔑 2. Multi-Factor Authentication (2FA / TOTP)
We provide an enterprise-ready Two-Factor Authentication system using Time-based One-time Passwords (TOTP):

1.  **Activation:** The user navigates to MFA settings, receives a secret key (base32) and scans the generated QR code.
2.  **TOTP Intercept Flow:**
    *   When MFA is active, entering the correct password during login does **not** log the user in immediately.
    *   Instead, they are redirected to a secure TOTP challenge page (`/accounts/2fa/authenticate/`).
    *   Entering the correct 6-digit code completes the session validation.
3.  **Backup Recovery Codes:** Users receive 10 single-use recovery codes in case they lose access to their authenticator app.

---

## 🛡️ 3. Security Headers & HSTS
To protect users from Clickjacking, Cross-Site Scripting (XSS), and session hijacking, the production middleware enforces:

*   **HSTS (HTTP Strict Transport Security):** Enforces HTTPS browser routing (`SECURE_HSTS_SECONDS = 31536000`).
*   **X-Frame-Options:** Prevents Clickjacking attacks by forbidding the site to be loaded inside an `<iframe>` (`X-Frame-Options = 'DENY'`).
*   **Content Security Policy (CSP):** Limits the execution of scripts to trusted origins.
