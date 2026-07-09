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

# التحقق مما إذا كان المشروع يعمل تحت بيئة الاختبارات (pytest)
TESTING = "test" in sys.argv or any("pytest" in arg for arg in sys.argv)

# تفعيل وضع التطوير الفوري لـ Vite (Hot Module Replacement) فقط خارج بيئة الاختبارات
DJANGO_VITE = {
    "default": {
        **DJANGO_VITE["default"],
        "dev_mode": not TESTING,
    }
}
