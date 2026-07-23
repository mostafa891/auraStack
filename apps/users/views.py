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
from django_ratelimit.decorators import ratelimit
from inertia import render, share

from apps.users.forms import AuraLoginForm, AuraRegisterForm, ProfileUpdateForm
from apps.users.services import AuthService, UserService
from common.utils.request import get_request_data


class LandingView(View):
    """عرض صفحة الهبوط العامة للقالب."""

    def get(self, request):
        return render(request, "Landing")


class LoginView(View):
    """تحكم تسجيل الدخول وإدارة حركة المرور مع التوجيه الذاتي."""

    def get(self, request):
        if request.user.is_authenticated:
            return redirect(reverse("profile"))
        return render(request, "Auth/Login")

    @method_decorator(ratelimit(key="ip", rate="10/m", method="POST", block=True))
    def post(self, request):
        if request.user.is_authenticated:
            return redirect(reverse("profile"))

        data = get_request_data(request)
        form = AuraLoginForm(data=data)

        if not form.is_valid():
            share(request, errors=form.errors.get_json_data())
            return render(request, "Auth/Login")

        result = AuthService.login_user(
            request=request,
            cleaned_email=form.cleaned_data["email"],
            password=form.cleaned_data["password"],
            remember=form.cleaned_data.get("remember", False),
        )

        if not result.success:
            share(request, errors=result.errors, error_code=result.code)
            return render(request, "Auth/Login")

        # إذا قام allauth بإرجاع استجابة توجيه مخصصة (مثل التوجيه للمصادقة الثنائية)، نقوم بإرجاعها
        if result.data:
            return result.data

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

    @method_decorator(ratelimit(key="ip", rate="10/m", method="POST", block=True))
    def post(self, request):
        if request.user.is_authenticated:
            return redirect(reverse("profile"))

        data = get_request_data(request)
        form = AuraRegisterForm(data=data)

        if not form.is_valid():
            share(request, errors=form.errors.get_json_data())
            return render(request, "Auth/Register")

        result = AuthService.register_user(
            request=request,
            cleaned_email=form.cleaned_data["email"],
            password=form.cleaned_data["password"],
        )

        if not result.success:
            share(request, errors=result.errors, error_code=result.code)
            return render(request, "Auth/Register")

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
            result = UserService.update_profile_preferences(
                user=request.user,
                language=form.cleaned_data["language"],
                theme=form.cleaned_data["theme"],
                timezone=form.cleaned_data["timezone"],
                avatar_url=form.cleaned_data.get("avatar_url"),
            )
            if result.success and hasattr(request, "session"):
                request.session["_language"] = request.user.language
            return redirect(reverse("profile"))
        else:
            share(request, errors=form.errors.get_json_data())
            return render(request, "Profile")


class LogoutView(View):
    """واجهة إنهاء الجلسة وتسجيل الخروج الآمن."""

    def post(self, request):
        auth_logout(request)
        return redirect(reverse("auth:login"))


class AvatarPresignView(View):
    """توليد روابط الرفع المباشر الموقعة للتخزين السحابي (أو محاكاتها محلياً في التطوير)."""

    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse(
                {"error": "Authentication credentials were not provided."}, status=401
            )

        # في بيئة الإنتاج: يمكن توليد رابط S3 Presigned POST هنا
        # في بيئة التطوير المحلية: نرجع رابط رفع محلي لمحاكاة المعاملة السحابية
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

    def _is_valid_image_header(self, uploaded_file) -> bool:
        """التحقق من صحة توقيع الصورة الفعلي (Magic Bytes) لتفادي التزوير."""
        header = uploaded_file.read(12)
        uploaded_file.seek(0)  # إعادة مؤشر الملف للبداية بعد القراءة

        # PNG
        if header.startswith(b"\x89PNG"):
            return True
        # JPEG
        if header.startswith(b"\xff\xd8\xff"):
            return True
        # GIF
        if header.startswith(b"GIF87a") or header.startswith(b"GIF89a"):
            return True
        # WEBP
        if len(header) >= 12 and header.startswith(b"RIFF") and header[8:12] == b"WEBP":
            return True

        return False

    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse(
                {"error": "Authentication credentials were not provided."}, status=401
            )

        # التحقق من مطابقة الـ user_id المرسل للمستخدم المصادق الحالي لمنع ثغرات التلاعب بالمعرفات
        user_id = request.POST.get("user_id")
        if not user_id or user_id != str(request.user.id):
            return JsonResponse({"error": "Access denied. User ID mismatch."}, status=403)

        if "file" not in request.FILES:
            return JsonResponse({"error": "No file uploaded"}, status=400)

        uploaded_file = request.FILES["file"]

        # 1. التحقق من امتداد الملف (Extension Whitelist)
        ext = os.path.splitext(uploaded_file.name)[1].lower()
        if ext not in [".png", ".jpg", ".jpeg", ".webp", ".gif"]:
            return JsonResponse(
                {
                    "error": (
                        "Invalid file extension. Only PNG, JPG, JPEG, WEBP, and GIF are allowed."
                    )
                },
                status=400,
            )

        # 2. التحقق من حجم الملف (الحد الأقصى 5 ميجابايت)
        if uploaded_file.size > 5 * 1024 * 1024:
            return JsonResponse({"error": "File size exceeds the limit of 5MB."}, status=400)

        # 3. التحقق من الـ Content-Type المرسل
        if not uploaded_file.content_type.startswith("image/"):
            return JsonResponse({"error": "File content type must be an image"}, status=400)

        # 4. التحقق الفعلي من توقيع الصورة (Magic Bytes)
        if not self._is_valid_image_header(uploaded_file):
            return JsonResponse({"error": "Corrupted or invalid image file structure"}, status=400)

        # توليد اسم فريد وحفظ الملف عبر نظام التخزين الافتراضي لدجانغو
        filename = f"avatars/{uuid.uuid4()}{ext}"
        saved_path = default_storage.save(filename, ContentFile(uploaded_file.read()))
        file_url = default_storage.url(saved_path)

        # إرجاع الرابط المطلق للملف
        absolute_url = request.build_absolute_uri(file_url)

        return JsonResponse({"avatar_url": absolute_url})
