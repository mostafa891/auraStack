from django.contrib import admin
from django.urls import include, path

from apps.users.views import ProfileView
from apps.users.views_security import (
    MfaAuthenticateView,
    MfaListView,
    PasswordChangeView,
    SocialConnectionsView,
    SocialSignupView,
    TotpActivateView,
    TotpDeactivateView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # توجيه مسارات المصادقة والـ Accounts إلى تطبيقنا الداخلي الموزع
    path("auth/", include("apps.users.urls", namespace="auth")),
    # صفحة تفضيلات الملف الشخصي الرئيسي
    path("profile/", ProfileView.as_view(), name="profile"),
    # تجاوز مسارات allauth الافتراضية بمسارات Inertia المخصصة على المستوى العام
    path("auth/password/change/", PasswordChangeView.as_view(), name="account_change_password"),
    path("auth/mfa/", MfaListView.as_view(), name="mfa_list"),
    path("auth/mfa/authenticate/", MfaAuthenticateView.as_view(), name="mfa_authenticate"),
    path("auth/mfa/totp/activate/", TotpActivateView.as_view(), name="mfa_activate_totp"),
    path("auth/mfa/totp/deactivate/", TotpDeactivateView.as_view(), name="mfa_deactivate_totp"),
    path(
        "auth/social/connections/",
        SocialConnectionsView.as_view(),
        name="socialaccount_connections",
    ),
    path("auth/social/signup/", SocialSignupView.as_view(), name="socialaccount_signup"),
    # تضمين مسارات django-allauth بالكامل للوصول لروابط المزايا الأمنية المتقدمة
    path("accounts/", include("allauth.urls")),
]
