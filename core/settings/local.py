from core.settings.base import *

# تفعيل الـ Debug والمؤشرات المحلية
DEBUG = env.bool("DEBUG", default=True)

# الالتزام بـ SQLite للمرحلة الحالية لتسريع التأسيس
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "LOCATION": BASE_DIR / "db.sqlite3",
    }
}
