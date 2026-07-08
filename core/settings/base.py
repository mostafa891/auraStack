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
]

LOCAL_APPS = [
    "apps.users.apps.UsersConfig",
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

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "users.CustomUser"

# معرّف الموقع الأساسي للمنصة (مطلوب لـ Sites Framework)
SITE_ID = 1

# خطوط دفاع المصادقة المعتمدة في دجانغو
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# ==============================================================================
# إعدادات الحداثة لـ django-allauth (المطابقة لتوثيق 2026 المحدث)
# ==============================================================================

# نسف وإسقاط حقل الـ username تماماً من خلايا الـ Backend
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USERNAME_REQUIRED = False

# المعيار الحديث لعام 2026: تحديد طرق الدخول كـ set صريحة
ACCOUNT_LOGIN_METHODS = {"email"}

# سياسات الحصانة الفريدة للجلسات والمستخدمين
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_SESSION_REMEMBER = True

# القيمة الافتراضية الصارمة للإنتاج (سيتم تعديلها محلياً في local للتطوير)
ACCOUNT_EMAIL_VERIFICATION = "mandatory"

# ==============================================================================
# Inertia.js — ربط Django بـ Vue عبر بروتوكول Inertia
# ==============================================================================

INERTIA_LAYOUT = "base.html"

# توافق CSRF مع Axios (المكتبة الداخلية لـ Inertia)
CSRF_HEADER_NAME = "HTTP_X_XSRF_TOKEN"
CSRF_COOKIE_NAME = "XSRF-TOKEN"

# ==============================================================================
# django-vite — إدارة الأصول المبنية بـ Vite
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
