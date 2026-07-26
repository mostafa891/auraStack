from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path

from apps.payments.api import private_api, public_api
from apps.users.views import LandingView, ProfileView
from apps.users.views_security import (
    MfaAuthenticateView,
    MfaListView,
    PasswordChangeView,
    PasswordResetDoneView,
    PasswordResetFromKeyDoneView,
    PasswordResetFromKeyView,
    PasswordResetView,
    SocialConnectionsView,
    SocialSignupView,
    TotpActivateView,
    TotpDeactivateView,
)
from common.views.health import health_check

urlpatterns = [
    path("", LandingView.as_view(), name="landing"),
    path("admin/", admin.site.urls),
    # API endpoints for payments and billing
    path("api/v1/private/", private_api.urls),
    path("api/v1/public/", public_api.urls),
    # Billing and subscriptions UI routes
    path("billing/", include("apps.payments.urls", namespace="billing")),
    # Authentication and accounts routing
    path("auth/", include("apps.users.urls", namespace="auth")),
    # Workspace and team management routes (Multi-tenancy)
    path("workspaces/", include("apps.teams.urls", namespace="teams")),
    # Blog and updates application routes
    path("blog/", include("apps.blog.urls", namespace="blog")),
    # User profile preferences page
    path("profile/", ProfileView.as_view(), name="profile"),
    # Override default allauth views with custom Inertia SPA views
    path("accounts/password/change/", PasswordChangeView.as_view(), name="account_change_password"),
    path("accounts/password/reset/", PasswordResetView.as_view(), name="account_reset_password"),
    path(
        "accounts/password/reset/done/",
        PasswordResetDoneView.as_view(),
        name="account_reset_password_done",
    ),
    re_path(
        r"^accounts/password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$",
        PasswordResetFromKeyView.as_view(),
        name="account_reset_password_from_key",
    ),
    path(
        "accounts/password/reset/key/done/",
        PasswordResetFromKeyDoneView.as_view(),
        name="account_reset_password_from_key_done",
    ),
    path("accounts/2fa/", MfaListView.as_view(), name="mfa_index"),
    path("accounts/2fa/authenticate/", MfaAuthenticateView.as_view(), name="mfa_authenticate"),
    path("accounts/2fa/totp/activate/", TotpActivateView.as_view(), name="mfa_activate_totp"),
    path("accounts/2fa/totp/deactivate/", TotpDeactivateView.as_view(), name="mfa_deactivate_totp"),
    path(
        "accounts/social/connections/",
        SocialConnectionsView.as_view(),
        name="socialaccount_connections",
    ),
    path("accounts/social/signup/", SocialSignupView.as_view(), name="socialaccount_signup"),
    # Include default allauth URL routes
    path("accounts/", include("allauth.urls")),
    # Health check endpoint
    path("health/", health_check, name="health_check"),
]

# Serve media files locally during development

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
