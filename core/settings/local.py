import logging
import os
import sys

from core.settings.base import *

# Enable local DEBUG mode
DEBUG = env.bool("DEBUG", default=True)

# Default SQLite database for local development
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Disable email verification requirements in local dev
ACCOUNT_EMAIL_VERIFICATION = "none"

# Console email backend for easy local testing
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Check if application is running under Pytest test runner
TESTING = (
    "test" in sys.argv
    or any("pytest" in arg for arg in sys.argv)
    or "PYTEST_CURRENT_TEST" in os.environ
    or "PYTEST_XDIST_WORKER" in os.environ
    or "pytest" in sys.modules
)

# Enable Vite Hot Module Replacement (HMR) in dev mode outside pytest
DJANGO_VITE = {
    "default": {
        **DJANGO_VITE["default"],
        "dev_mode": not TESTING,
    }
}

# ==============================================================================
# Query performance monitoring and N+1 query detection
# ==============================================================================
if DEBUG:
    # 1. Setup django-querycount middleware
    MIDDLEWARE.insert(0, "querycount.middleware.QueryCountMiddleware")
    QUERYCOUNT = {
        "THRESHOLDS": {
            "MEDIUM": 5,
            "HIGH": 10,
            "MIN_TIME_TO_LOG": 0,
            "MIN_QUERY_COUNT_TO_LOG": 2,
        },
        "IGNORE_REQUESTS": [],
        "IGNORE_SQL_PATTERNS": [],
        "DISPLAY_DUPLICATES": True,
    }

    # 2. Setup nplusone lazy-query detection
    INSTALLED_APPS.insert(0, "nplusone.ext.django")
    MIDDLEWARE.insert(0, "nplusone.ext.django.NPlusOneMiddleware")

    NPLUSONE_LOGGER = logging.getLogger("django")
    NPLUSONE_LOG_LEVEL = logging.WARNING
    NPLUSONE_RAISE = TESTING  # Raise error immediately during test execution on N+1 queries
    NPLUSONE_WHITELIST = [
        {"model": "teams.Workspace", "field": "subscription"},
        {"model": "Workspace", "field": "subscription"},
        {"model": "apps.teams.models.Workspace", "field": "subscription"},
    ]

# Disable rate limiting during automated test execution
RATELIMIT_ENABLE = not TESTING
