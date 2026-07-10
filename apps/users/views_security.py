import json

from allauth.account.forms import ChangePasswordForm
from allauth.account.internal.decorators import login_stage_required
from allauth.mfa.adapter import get_adapter
from allauth.mfa.base.forms import AuthenticateForm
from allauth.mfa.models import Authenticator
from allauth.mfa.stages import AuthenticateStage
from allauth.mfa.totp.forms import ActivateTOTPForm, DeactivateTOTPForm
from allauth.socialaccount.forms import DisconnectForm
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers import registry
from allauth.socialaccount.views import SignupView as AllauthSocialSignupView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from inertia import render, share


def get_request_data(request) -> dict:
    """استخراج بيانات الطلب سواء كانت JSON أو Form-Encoded بأمان لتوافق Inertia."""
    if request.content_type == "application/json":
        try:
            return json.loads(request.body)
        except json.JSONDecodeError:
            return {}
    return request.POST


# ==============================================================================
# Password Change — تغيير كلمة المرور (Pure SPA)
# ==============================================================================


class PasswordChangeView(LoginRequiredMixin, View):
    """تغيير كلمة المرور عبر Inertia."""

    def get(self, request):
        return render(request, "Security/PasswordChange")

    def post(self, request):
        data = get_request_data(request)

        # خريطة تحويل الحقول لتطابق مسميات النموذج الداخلي لـ allauth
        mapped_data = {
            "oldpassword": data.get("old_password"),
            "password1": data.get("password"),
            "password2": data.get("password_confirm"),
        }

        form = ChangePasswordForm(user=request.user, data=mapped_data)

        if form.is_valid():
            form.save()
            # إنهاء التغيير وتحديث الجلسة وإرسال التنبيهات الرسمية لـ allauth
            from allauth.account.internal.flows.password_change import finalize_password_change

            finalize_password_change(request, form.user)
            return redirect(reverse("profile"))
        else:
            # إعادة خريطة مسميات الأخطاء لتظهر في الواجهة الأمامية بشكل صحيح
            errors = form.errors.get_json_data()
            mapped_errors = {}
            if "oldpassword" in errors:
                mapped_errors["old_password"] = errors["oldpassword"]
            if "password1" in errors:
                mapped_errors["password"] = errors["password1"]
            if "password2" in errors:
                mapped_errors["password_confirm"] = errors["password2"]

            share(request, errors=mapped_errors)
            return redirect(reverse("auth:password_change"))


# ==============================================================================
# MFA Index — قائمة أجهزة المصادقة الثنائية (2FA)
# ==============================================================================


class MfaListView(LoginRequiredMixin, View):
    """عرض وإدارة المصادقة الثنائية (2FA) عبر Inertia."""

    def get(self, request):
        totp_active = Authenticator.objects.filter(
            user=request.user, type=Authenticator.Type.TOTP
        ).exists()

        return render(
            request,
            "Security/MfaList",
            {
                "totp_active": totp_active,
            },
        )


# ==============================================================================
# TOTP Activate — تفعيل المصادقة الثنائية
# ==============================================================================


class TotpActivateView(LoginRequiredMixin, View):
    """تفعيل TOTP/2FA عبر Inertia."""

    def get(self, request):
        # التحقق مما إذا كان مفعلاً بالفعل لتفادي التكرار
        if Authenticator.objects.filter(user=request.user, type=Authenticator.Type.TOTP).exists():
            return redirect(reverse("auth:mfa_list"))

        # إنشاء فورم Allauth الافتراضي لتوليد الـ secret تلقائياً
        form = ActivateTOTPForm(user=request.user)
        adapter = get_adapter()
        totp_url = adapter.build_totp_url(request.user, form.secret)
        totp_svg = adapter.build_totp_svg(totp_url)

        # حفظ الـ secret في الـ session لمطابقته في الـ POST
        request.session["totp_secret"] = form.secret

        return render(
            request,
            "Security/TotpActivate",
            {
                "totp_svg": totp_svg,
                "totp_key": form.secret,
            },
        )

    def post(self, request):
        secret = request.session.get("totp_secret")
        if not secret:
            return redirect(reverse("auth:totp_activate"))

        data = get_request_data(request)
        form = ActivateTOTPForm(user=request.user, data=data)
        form.secret = secret  # تمرير الـ secret المخزن لمطابقته

        if form.is_valid():
            from allauth.mfa.totp.internal import flows

            flows.activate_totp(request, form)
            request.session.pop("totp_secret", None)
            return redirect(reverse("auth:mfa_list"))
        else:
            share(request, errors=form.errors.get_json_data())
            return redirect(reverse("auth:totp_activate"))


# ==============================================================================
# TOTP Deactivate — تعطيل المصادقة الثنائية
# ==============================================================================


class TotpDeactivateView(LoginRequiredMixin, View):
    """تعطيل TOTP/2FA عبر Inertia."""

    def get_authenticator(self, request):
        return get_object_or_404(Authenticator, user=request.user, type=Authenticator.Type.TOTP)

    def get(self, request):
        self.get_authenticator(request)  # التحقق من الوجود
        return render(request, "Security/TotpDeactivate")

    def post(self, request):
        authenticator = self.get_authenticator(request)
        data = get_request_data(request)

        # فورم التعطيل يتطلب تمرير الـ authenticator
        form = DeactivateTOTPForm(authenticator=authenticator, data=data)

        if form.is_valid():
            from allauth.mfa.totp.internal import flows

            flows.deactivate_totp(request, authenticator)
            return redirect(reverse("auth:mfa_list"))
        else:
            share(request, errors=form.errors.get_json_data())
            return redirect(reverse("auth:totp_deactivate"))


# ==============================================================================
# MFA Authenticate — التحقق من رمز MFA أثناء تسجيل الدخول
# ==============================================================================


@method_decorator(
    login_stage_required(stage=AuthenticateStage.key, redirect_urlname="auth:login"),
    name="dispatch",
)
class MfaAuthenticateView(View):
    """التحقق من رمز MFA أثناء تسجيل الدخول عبر Inertia."""

    def get(self, request):
        return render(request, "Security/MfaAuthenticate")

    def post(self, request):
        stage = request._login_stage
        user = stage.login.user
        data = get_request_data(request)

        form = AuthenticateForm(user=user, data=data)

        if form.is_valid():
            form.save()
            return stage.exit()  # إنهاء عملية تسجيل الدخول وتوجيه المستخدم للداخل
        else:
            share(request, errors=form.errors.get_json_data())
            return redirect(reverse("auth:mfa_authenticate"))


# ==============================================================================
# Social Connections — إدارة الحسابات الاجتماعية المرتبطة
# ==============================================================================


class SocialConnectionsView(LoginRequiredMixin, View):
    """إدارة الحسابات الاجتماعية المرتبطة عبر Inertia."""

    def get(self, request):
        social_accounts = SocialAccount.objects.filter(user=request.user)
        accounts = []
        for account in social_accounts:
            accounts.append(
                {
                    "id": account.id,
                    "provider": account.provider,
                    "uid": account.uid,
                }
            )

        providers = []
        for provider_class in registry.get_class_list():
            providers.append(
                {
                    "id": provider_class.id,
                    "name": provider_class.name,
                }
            )

        return render(
            request,
            "Security/SocialConnections",
            {
                "accounts": accounts,
                "providers": providers,
            },
        )

    def post(self, request):
        data = get_request_data(request)
        form = DisconnectForm(request=request, data=data)

        if form.is_valid():
            form.save()
            return redirect(reverse("auth:social_connections"))
        else:
            share(request, errors=form.errors.get_json_data())
            return redirect(reverse("auth:social_connections"))


# ==============================================================================
# Social Signup — استكمال التسجيل للحسابات الاجتماعية
# ==============================================================================


class SocialSignupView(AllauthSocialSignupView):
    """استكمال الاشتراك للحسابات الاجتماعية عبر Inertia."""

    def render_to_response(self, context, **response_kwargs):
        provider = context.get("account").provider if context.get("account") else ""
        return render(self.request, "Auth/SocialSignup", {"provider": provider})

    def form_invalid(self, form):
        share(self.request, errors=form.errors.get_json_data())
        return redirect(self.request.path)
