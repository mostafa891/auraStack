# Error Handling & Rate Limiting

This document details the standards, response formats, and security policies for error handling, user input validation, and rate limiting in AuraStack.

---

## 📋 1. Standard API Error Response

All API endpoints (built via Django Ninja) return a unified JSON payload when an error occurs. This makes it predictable for the frontend SPA to display error messages.

*   **Standard Format:**
    ```json
    {
      "message": "Detailed developer or user-friendly error message",
      "code": "ERROR_CODE",
      "errors": {
        "field_name": [
          {
            "message": "Field specific validation error",
            "code": "invalid_format"
          }
        ]
      }
    }
    ```

---

## 🛡️ 2. Rate Limiting Protection

AuraStack implements endpoint protection using `django-ratelimit` to protect sensitive authentication pages and payment workflows from brute-force and spam attacks.

### Configuration
We configure IP-based rate limiting on mutation methods:
```python
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit

class LoginView(View):
    @method_decorator(ratelimit(key="ip", rate="10/m", method="POST", block=True))
    def post(self, request):
        # processes auth requests...
```

### Request Blocking
*   **Triggered limits:** If a client exceeds the limit (e.g., more than 10 requests in a minute on auth views), Django raises a `RatelimitLimited` exception.
*   **Response:** By default, Django returns an HTTP 403 (Forbidden) page, which is captured and formatted cleanly.

---

## 📝 3. Logging & Sentry Integration

### Sentry Integration
In production, we integrate Sentry SDK to capture all unhandled exceptions (HTTP 500) automatically, generating trace logs without exposing customer secrets.

*   **Activation:** Set `SENTRY_DSN` in your environment.
*   **Privacy:** Configured with `send_default_pii=False` to comply with privacy laws (GDPR/HIPAA).

### Structured Logging
In production, log formats can be formatted to JSON (e.g., using `python-json-logger`) to interface easily with centralized metrics processors like Datadog, AWS CloudWatch, or Google Cloud Logging.
