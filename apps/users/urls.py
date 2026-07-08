from django.urls import path

from apps.users.views import LoginView, LogoutView, ProfileUpdateView, RegisterView

app_name = "auth"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("register/", RegisterView.as_view(), name="register"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/update/", ProfileUpdateView.as_view(), name="profile_update"),
]
