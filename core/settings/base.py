from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent


environ.Env.read_env(str(BASE_DIR / ".env"))
env = environ.Env()

SECRET_KEY = env("SECRET_KEY")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])


DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "django_cleanup.apps.CleanupConfig",
    "django_extensions",
    "django_vite",
    "inertia",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.github",
    "allauth.mfa",
    "django_q",
    "anymail",
]

LOCAL_APPS = [
    "apps.users.apps.UsersConfig",
    "apps.teams.apps.TeamsConfig",
    "apps.payments.apps.PaymentsConfig",
    "apps.blog.apps.BlogConfig",
]

INSTALLED_APPS = (
    [
        "unfold",
        "unfold.contrib.filters",
    ]
    + DJANGO_APPS
    + THIRD_PARTY_APPS
    + LOCAL_APPS
)

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "inertia.middleware.InertiaMiddleware",
    "common.middleware.ShareUserDataMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"
ASGI_APPLICATION = "core.asgi.application"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en"
LANGUAGES = [
    ("en", "English"),
    ("ar", "Arabic"),
]
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "users.CustomUser"

# Primary Site ID for Sites Framework
SITE_ID = 1

# Authentication Backends
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# ==============================================================================
# django-allauth Settings
# ==============================================================================

# Exclude username field from backend user model
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]

# Login methods configuration
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_ADAPTER = "apps.users.adapters.allauth.CustomAccountAdapter"

# Session and user security policies
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_SESSION_REMEMBER = True

# Production default email verification policy
ACCOUNT_EMAIL_VERIFICATION = "mandatory"

# Post-login and logout redirects
LOGIN_REDIRECT_URL = "profile"
LOGOUT_REDIRECT_URL = "auth:login"

# ==============================================================================
# Inertia.js Settings
# ==============================================================================

INERTIA_LAYOUT = "base.html"

# CSRF header compatibility for Axios (Inertia HTTP client)
CSRF_HEADER_NAME = "HTTP_X_XSRF_TOKEN"
CSRF_COOKIE_NAME = "XSRF-TOKEN"

# ==============================================================================
# django-vite Settings
# ==============================================================================

DJANGO_VITE = {
    "default": {
        "dev_mode": False,
        "dev_server_host": "localhost",
        "dev_server_port": 5173,
        "manifest_path": BASE_DIR / "static" / "dist" / ".vite" / "manifest.json",
        "static_url_prefix": "dist",
    }
}

# ==============================================================================
# Logging Configuration
# ==============================================================================

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {asctime} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
        "aurastack.security": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "aurastack.audit": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# ==============================================================================
# Social Account Providers Configuration
# ==============================================================================

SOCIALACCOUNT_LOGIN_ON_GET = False
SOCIALACCOUNT_AUTO_SIGNUP = True

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": env.str("GOOGLE_CLIENT_ID", default=""),
            "secret": env.str("GOOGLE_CLIENT_SECRET", default=""),
            "key": "",
        },
        "SCOPE": [
            "profile",
            "email",
        ],
        "AUTH_PARAMS": {
            "access_type": "online",
        },
    },
    "github": {
        "APP": {
            "client_id": env.str("GITHUB_CLIENT_ID", default=""),
            "secret": env.str("GITHUB_CLIENT_SECRET", default=""),
            "key": "",
        },
        "SCOPE": [
            "user",
            "read:user",
            "user:email",
        ],
    },
}

REDIS_URL = env.str("REDIS_URL", default="")

if REDIS_URL:
    Q_CLUSTER = {
        "name": "aurastack_q",
        "workers": 4,
        "recycle": 500,
        "timeout": 60,
        "redis": REDIS_URL,
    }
else:
    Q_CLUSTER = {
        "name": "aurastack_q",
        "workers": 2,
        "recycle": 100,
        "timeout": 60,
        "sleep": 1,  # Gentle polling interval to prevent local CPU database strain
        "save_limit": 0,  # Prune successful tasks immediately to prevent database bloat
        "orm": "default",
    }


# ==============================================================================
# Stripe and Billing Settings
# ==============================================================================
STRIPE_PUBLISHABLE_KEY = env.str("STRIPE_PUBLISHABLE_KEY", default="")
STRIPE_SECRET_KEY = env.str("STRIPE_SECRET_KEY", default="")
STRIPE_WEBHOOK_SECRET = env.str("STRIPE_WEBHOOK_SECRET", default="")

DEFAULT_PAYMENT_PROVIDER = env.str("DEFAULT_PAYMENT_PROVIDER", default="STRIPE")

# ==============================================================================
# Anymail (Resend) Settings
# ==============================================================================
ANYMAIL = {
    "RESEND_API_KEY": env.str("RESEND_API_KEY", default=""),
}

# ==============================================================================
# Cache Settings (Required for django-ratelimit)
# ==============================================================================
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    }
}

# ==============================================================================
# Unfold Admin Panel Settings
# ==============================================================================
UNFOLD = {
    "DASHBOARD_CALLBACK": "common.admin_dashboard.admin_dashboard_callback",
}
