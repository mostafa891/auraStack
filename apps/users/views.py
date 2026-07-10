import json
import os
import uuid

from django.contrib.auth import logout as auth_logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from inertia import render, share

from apps.users.forms import AuraLoginForm, AuraRegisterForm, ProfileUpdateForm
from apps.users.services import AuthService


def get_request_data(request) -> dict:
    """استخراج بيانات الطلب سواء كانت JSON أو Form-Encoded بأمان."""
    if request.content_type == "application/json":
        try:
            return json.loads(request.body)
        except json.JSONDecodeError:
            return {}
    return request.POST


class LoginView(View):
    """تحكم تسجيل الدخول وإدارة حركة المرور مع التوجيه الذاتي."""

    def get(self, request):
        if request.user.is_authenticated:
            return redirect(reverse("profile"))
        return render(request, "Auth/Login")

    def post(self, request):
        if request.user.is_authenticated:
            return redirect(reverse("profile"))

        data = get_request_data(request)
        form = AuraLoginForm(data=data)

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

        pending_token = request.session.get("pending_invite_token")
        if pending_token:
            return redirect(reverse("teams:accept_invitation", kwargs={"token": pending_token}))

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

        data = get_request_data(request)
        form = AuraRegisterForm(data=data)

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

        pending_token = request.session.get("pending_invite_token")
        if pending_token:
            return redirect(reverse("teams:accept_invitation", kwargs={"token": pending_token}))

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
        data = get_request_data(request)
        form = ProfileUpdateForm(data=data, instance=request.user)

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


class AvatarPresignView(LoginRequiredMixin, View):
    """توليد روابط الرفع المباشر الموقعة للتخزين السحابي (أو محاكاتها محلياً في التطوير)."""

    login_url = "auth:login"

    def get(self, request):
        # في بيئة الإنتاج: يمكن توليد رابط S3 Presigned POST هنا
        # في بيئة التطوير المحلية: نرجع رابط رفع محلي لمحاكاة المعاملة السحابية
        from django.urls import reverse

        upload_url = request.build_absolute_uri(reverse("auth:avatar_upload"))
        return JsonResponse(
            {
                "upload_url": upload_url,
                "method": "POST",
                "fields": {
                    "user_id": str(request.user.id),
                },
            }
        )


@method_decorator(csrf_exempt, name="dispatch")
class AvatarUploadView(View):
    """مستقبل الرفع المباشر للملفات الثنائية (محاكاة السحابة للتطوير المحلي)."""

    def post(self, request):
        if "file" not in request.FILES:
            return JsonResponse({"error": "No file uploaded"}, status=400)

        uploaded_file = request.FILES["file"]

        # التحقق من أن الملف صورة
        if not uploaded_file.content_type.startswith("image/"):
            return JsonResponse({"error": "File must be an image"}, status=400)

        # توليد اسم فريد وحفظ الملف عبر نظام التخزين الافتراضي لدجانغو (يدعم التحويل لـ S3 تلقائياً)
        ext = os.path.splitext(uploaded_file.name)[1] or ".png"
        filename = f"avatars/{uuid.uuid4()}{ext}"

        saved_path = default_storage.save(filename, ContentFile(uploaded_file.read()))
        file_url = default_storage.url(saved_path)

        # إرجاع الرابط المطلق للملف
        absolute_url = request.build_absolute_uri(file_url)

        return JsonResponse({"avatar_url": absolute_url})
