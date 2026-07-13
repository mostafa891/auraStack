import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from core.settings.base import *

DEBUG = False

# HTTPS & Security Settings
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# HSTS Configuration
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# X-Frame-Options & Browsers policies
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"

# Allowed Hosts
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

# WhiteNoise production configuration (Static files caching) & Cloud Storage
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

USE_S3_STORAGE = env.bool("USE_S3_STORAGE", default=False)
if USE_S3_STORAGE:
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }
    AWS_ACCESS_KEY_ID = env.str("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = env.str("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = env.str("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_ENDPOINT_URL = env.str("AWS_S3_ENDPOINT_URL", default=None)
    AWS_S3_CUSTOM_DOMAIN = env.str("AWS_S3_CUSTOM_DOMAIN", default=None)
    AWS_S3_SIGNATURE_VERSION = "s3v4"  # إلزامي لخدمة Cloudflare R2
    AWS_S3_FILE_OVERWRITE = False
    AWS_S3_OBJECT_PARAMETERS = {
        "CacheControl": "max-age=86400",
    }
else:
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }

# تهيئة الـ Redis Cache في الإنتاج ليدعم عمل الـ Rate limiting عبر الحاويات الموزعة
REDIS_URL = env.str("REDIS_URL", default="")
if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": REDIS_URL,
        }
    }


# Production database (PostgreSQL by default)
DATABASES = {
    "default": {
        **env.db("DATABASE_URL"),
        "CONN_MAX_AGE": 60,
    }
}

# sentry-sdk integration

SENTRY_DSN = env.str("SENTRY_DSN", default="")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=1.0,
        send_default_pii=False,
    )

# Email Backend in Production
EMAIL_BACKEND = env.str("EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend")
if EMAIL_BACKEND == "django.core.mail.backends.smtp.EmailBackend":
    EMAIL_HOST = env.str("EMAIL_HOST", default="")
    EMAIL_PORT = env.int("EMAIL_PORT", default=587)
    EMAIL_HOST_USER = env.str("EMAIL_HOST_USER", default="")
    EMAIL_HOST_PASSWORD = env.str("EMAIL_HOST_PASSWORD", default="")
    EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)

DEFAULT_FROM_EMAIL = env.str("DEFAULT_FROM_EMAIL", default="webmaster@localhost")
