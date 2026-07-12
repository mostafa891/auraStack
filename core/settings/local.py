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

# طباعة رسائل البريد الإلكتروني في الكونسول لتسهيل التطوير المحلي واختبار الروابط
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# التحقق مما إذا كان المشروع يعمل تحت بيئة الاختبارات (pytest)
TESTING = "test" in sys.argv or any("pytest" in arg for arg in sys.argv)

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
    NPLUSONE_LOGGER = "django"
    NPLUSONE_LOG_LEVEL = "WARNING"
    NPLUSONE_RAISE = (
        TESTING  # إيقاف الاختبار وإفشاله فوراً إذا تم رصد N+1، وطباعة تحذير فقط في التصفح المعتاد
    )
