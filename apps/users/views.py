from django.contrib.auth import logout as auth_logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from inertia import render, share

from apps.users.forms import AuraLoginForm, AuraRegisterForm, ProfileUpdateForm
from apps.users.services import AuthService


class LoginView(View):
    """تحكم تسجيل الدخول وإدارة حركة المرور مع التوجيه الذاتي."""

    def get(self, request):
        if request.user.is_authenticated:
            return redirect(reverse("profile"))
        return render(request, "Auth/Login")

    def post(self, request):
        if request.user.is_authenticated:
            return redirect(reverse("profile"))

        form = AuraLoginForm(data=request.POST)

        if not form.is_valid():
            share(request, errors=form.errors.get_json_data())
            return redirect(reverse("auth:login"))

        result = AuthService.login_user(
            request=request,
            cleaned_email=form.cleaned_data["email"],
            password=form.cleaned_data["password"],
        )

        if not result.success:
            share(request, errors=result.errors, error_code=result.code)
            return redirect(reverse("auth:login"))

        return redirect(reverse("profile"))


class RegisterView(View):
    """تحكم إنشاء حساب جديد مع التوجيه الذاتي للمستخدمين المصادقين."""

    def get(self, request):
        if request.user.is_authenticated:
            return redirect(reverse("profile"))
        return render(request, "Auth/Register")

    def post(self, request):
        if request.user.is_authenticated:
            return redirect(reverse("profile"))

        form = AuraRegisterForm(data=request.POST)

        if not form.is_valid():
            share(request, errors=form.errors.get_json_data())
            return redirect(reverse("auth:register"))

        result = AuthService.register_user(
            request=request,
            cleaned_email=form.cleaned_data["email"],
            password=form.cleaned_data["password"],
        )

        if not result.success:
            share(request, errors=result.errors, error_code=result.code)
            return redirect(reverse("auth:register"))

        return redirect(reverse("profile"))


class ProfileView(LoginRequiredMixin, View):
    """صفحة التفضيلات الشخصية وإعدادات الحساب للمستخدم."""

    login_url = "auth:login"

    def get(self, request):
        return render(request, "Profile")


class ProfileUpdateView(LoginRequiredMixin, View):
    """مستقبل تحديث تفضيلات المستخدم (اللغة، المظهر، المنطقة الزمنية)."""

    login_url = "auth:login"

    def post(self, request):
        form = ProfileUpdateForm(data=request.POST, instance=request.user)

        if form.is_valid():
            form.save()
        else:
            share(request, errors=form.errors.get_json_data())

        return redirect(reverse("profile"))


class LogoutView(View):
    """واجهة إنهاء الجلسة وتسجيل الخروج الآمن."""

    def get(self, request):
        auth_logout(request)
        return redirect(reverse("auth:login"))

    def post(self, request):
        auth_logout(request)
        return redirect(reverse("auth:login"))
