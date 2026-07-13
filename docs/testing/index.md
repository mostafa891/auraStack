# Testing Architecture & Verification

This document details the testing architecture, runner options, advanced test categories, and automated verification suites in AuraStack.

---

## 🧪 1. Testing Frameworks

AuraStack enforces extreme code quality and prevents regressions using a comprehensive testing stack:

*   **Pytest:** Standard Python test runner.
*   **Pytest-Django:** Handles database isolation via rollbacks and fixtures.
*   **Playwright:** Automated cross-browser E2E testing (simulating user actions in chromium/firefox).
*   **CaptureQueriesContext:** Django query inspector to capture and assert N+1 regressions.

---

## 🏃 2. Running Tests

### Automated Verification Script (Recommended)
We provide a unified verification script that installs packages, checks migrations, and runs the entire test suite in one command:
```bash
python verify_all.py
```

### Manual Pytest Run
Run all tests inside transactions with database rollbacks:
```bash
pytest
```

### Run Playwright E2E Browser Tests
Runs frontend integration tests inside simulated browsers:
```bash
pytest tests/e2e/
```

---

## 🛡️ 3. Advanced Test Categories (CTO-Hardened)

To make AuraStack the most secure and reliable boilerplate, the test suite includes critical security and performance test files:

### A. Database N+1 Regression Testing (`tests/test_nplusone_regressions.py`)
Ensures list views (like Workspace settings and membership lists) run in $O(1)$ database query complexity. Adding members to a workspace does not increase the query count, preventing performance degradation at scale.

### B. Multi-Tenant BOLA / IDOR Isolation (`tests/test_tenant_isolation.py`)
Rigorously checks that data cannot leak between workspaces. Verifies that user A in Workspace A cannot access Workspace B's views, update its settings, or send workspace invitations.

### C. Webhook Signature Security (`tests/test_webhook_security.py`)
Tests webhook endpoint security against replay attacks and faked signature headers. Ensures payloads with invalid HMAC headers raise `ValueError` and are rejected.

### D. Workspace Lockout & Limits (`tests/test_workspace_lockout.py`)
Verifies that when a workspace exceeds its plan limits (e.g., more than 3 members on a free plan, or a canceled Pro subscription), the middleware correctly flags `is_locked = True` to notify the SPA.
