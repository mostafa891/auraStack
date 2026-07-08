from django.contrib import admin
from django.urls import include, path

from apps.users.views import ProfileView

urlpatterns = [
    path("admin/", admin.site.urls),
    # توجيه مسارات المصادقة والـ Accounts إلى تطبيقنا الداخلي الموزع
    path("auth/", include("apps.users.urls", namespace="auth")),
    # صفحة تفضيلات الملف الشخصي الرئيسي
    path("profile/", ProfileView.as_view(), name="profile"),
    # تضمين مسارات django-allauth بالكامل للوصول لروابط المزايا الأمنية المتقدمة
    path("accounts/", include("allauth.urls")),
]
