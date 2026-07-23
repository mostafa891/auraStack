import logging
import os
import sys

from core.settings.base import *

# تفعيل الـ Debug والمؤشرات المحلية
DEBUG = env.bool("DEBUG", default=True)

# الالتزام بـ SQLite للمرحلة الحالية لتسريع التأسيس
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# تعطيل التحقق من البريد تماماً في بيئة التطوير المحلية لتسريع بناء الواجهات
ACCOUNT_EMAIL_VERIFICATION = "none"

# طباعة رسائل البريد الإلكتروني في الكونسول لتسهيل التطوير المحلي وااختبار الروابط
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# التحقق مما إذا كان المشروع يعمل تحت بيئة الاختبارات (pytest)
TESTING = (
    "test" in sys.argv
    or any("pytest" in arg for arg in sys.argv)
    or "PYTEST_CURRENT_TEST" in os.environ
    or "PYTEST_XDIST_WORKER" in os.environ
    or "pytest" in sys.modules
)

# تفعيل وضع التطوير الفوري لـ Vite (Hot Module Replacement) فقط خارج بيئة الاختبارات
DJANGO_VITE = {
    "default": {
        **DJANGO_VITE["default"],
        "dev_mode": not TESTING,
    }
}

# ==============================================================================
# أدوات مراقبة الاستعلامات وتتبع مشاكل N+1 في بيئة التطوير والاختبار
# ==============================================================================
if DEBUG:
    # 1. إعداد django-querycount لمراقبة عدد الاستعلامات وتكرارها في الطرفية
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

    # 2. إعداد nplusone لاكتشاف الاستعلامات الكسولة وتنبيهك بها
    INSTALLED_APPS.insert(0, "nplusone.ext.django")
    MIDDLEWARE.insert(0, "nplusone.ext.django.NPlusOneMiddleware")

    NPLUSONE_LOGGER = logging.getLogger("django")
    NPLUSONE_LOG_LEVEL = logging.WARNING
    NPLUSONE_RAISE = (
        TESTING  # إيقاف الاختبار وإفشاله فوراً إذا تم رصد N+1، وطباعة تحذير فقط في التصفح المعتاد
    )
    NPLUSONE_WHITELIST = [
        {"model": "teams.Workspace", "field": "subscription"},
        {"model": "Workspace", "field": "subscription"},
        {"model": "apps.teams.models.Workspace", "field": "subscription"},
    ]

# تعطيل محدد معدل الطلبات أثناء الاختبارات لمنع حظر اختبارات E2E والـ Live Server
RATELIMIT_ENABLE = not TESTING
