from django.urls import path

from apps.users.views import LoginView, LogoutView, ProfileUpdateView, RegisterView
from apps.users.views_security import (
    MfaAuthenticateView,
    MfaListView,
    PasswordChangeView,
    SocialConnectionsView,
    TotpActivateView,
    TotpDeactivateView,
)

app_name = "auth"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("register/", RegisterView.as_view(), name="register"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/update/", ProfileUpdateView.as_view(), name="profile_update"),
    # Security, MFA, and Social connections (SPA Vue/Inertia pages)
    path("password/change/", PasswordChangeView.as_view(), name="password_change"),
    path("mfa/", MfaListView.as_view(), name="mfa_list"),
    path("mfa/authenticate/", MfaAuthenticateView.as_view(), name="mfa_authenticate"),
    path("mfa/totp/activate/", TotpActivateView.as_view(), name="totp_activate"),
    path("mfa/totp/deactivate/", TotpDeactivateView.as_view(), name="totp_deactivate"),
    path("social/connections/", SocialConnectionsView.as_view(), name="social_connections"),
]
