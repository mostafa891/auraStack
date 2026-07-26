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
    """Renders the public landing page for the application."""

    def get(self, request):
        return render(request, "Landing")


class LoginView(View):
    """Handles user authentication and traffic routing with self-redirects."""

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

        # Handle custom redirect responses returned by django-allauth (e.g. 2FA MFA redirect)
        if result.data:
            return result.data

        pending_token = request.session.get("pending_invite_token")
        if pending_token:
            return redirect(reverse("teams:accept_invitation", kwargs={"token": pending_token}))

        return redirect(reverse("profile"))


class RegisterView(View):
    """Handles user registration with self-redirects for authenticated users."""

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
    """User profile and account settings page."""

    login_url = "auth:login"

    def get(self, request):
        return render(request, "Profile")


class ProfileUpdateView(LoginRequiredMixin, View):
    """Updates user profile preferences (language, theme, timezone, avatar)."""

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
    """Ends user session and logs out safely."""

    def post(self, request):
        auth_logout(request)
        return redirect(reverse("auth:login"))


class AvatarPresignView(View):
    """Generates direct signed upload URLs for cloud storage (or local dev simulation)."""

    def get(self, request):
        if not request.user.is_authenticated:
            return JsonResponse(
                {"error": "Authentication credentials were not provided."}, status=401
            )

        # In production: generate S3 Presigned POST URL here
        # In local development: return local upload URL to simulate cloud behavior
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
    """Endpoint for direct binary file uploads (simulating cloud storage in local dev)."""

    def _is_valid_image_header(self, uploaded_file) -> bool:
        """Validates actual file header magic bytes to prevent spoofing."""
        header = uploaded_file.read(12)
        uploaded_file.seek(0)  # Reset stream position after reading

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

        # Verify uploaded user_id matches authenticated user to prevent IDOR vulnerabilities
        user_id = request.POST.get("user_id")
        if not user_id or user_id != str(request.user.id):
            return JsonResponse({"error": "Access denied. User ID mismatch."}, status=403)

        if "file" not in request.FILES:
            return JsonResponse({"error": "No file uploaded"}, status=400)

        uploaded_file = request.FILES["file"]

        # 1. File extension whitelist check
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

        # 2. File size limit check (Max 5MB)
        if uploaded_file.size > 5 * 1024 * 1024:
            return JsonResponse({"error": "File size exceeds the limit of 5MB."}, status=400)

        # 3. Content-Type check
        if not uploaded_file.content_type.startswith("image/"):
            return JsonResponse({"error": "File content type must be an image"}, status=400)

        # 4. Magic bytes signature verification
        if not self._is_valid_image_header(uploaded_file):
            return JsonResponse({"error": "Corrupted or invalid image file structure"}, status=400)

        # Generate unique filename and save via Django default storage
        filename = f"avatars/{uuid.uuid4()}{ext}"
        saved_path = default_storage.save(filename, ContentFile(uploaded_file.read()))
        file_url = default_storage.url(saved_path)

        # Return absolute URL for the saved avatar image
        absolute_url = request.build_absolute_uri(file_url)

        return JsonResponse({"avatar_url": absolute_url})


@method_decorator(csrf_exempt, name="dispatch")
class AvatarDeleteView(LoginRequiredMixin, View):
    """Deletes avatar image file and resets avatar URL for authenticated user."""

    def post(self, request):
        user = request.user
        if user.avatar_url:
            if "/media/" in user.avatar_url:
                relative_path = user.avatar_url.split("/media/")[-1]
                if default_storage.exists(relative_path):
                    default_storage.delete(relative_path)
            user.avatar_url = ""
            user.save(update_fields=["avatar_url"])

        return JsonResponse({"success": True, "avatar_url": ""})
