from allauth.account.forms import ChangePasswordForm
from allauth.account.internal.decorators import login_stage_required
from allauth.account.views import (
    PasswordResetDoneView as AllauthPasswordResetDoneView,
)
from allauth.account.views import (
    PasswordResetFromKeyDoneView as AllauthPasswordResetFromKeyDoneView,
)
from allauth.account.views import (
    PasswordResetFromKeyView as AllauthPasswordResetFromKeyView,
)
from allauth.account.views import (
    PasswordResetView as AllauthPasswordResetView,
)
from allauth.mfa.adapter import get_adapter
from allauth.mfa.base.forms import AuthenticateForm
from allauth.mfa.stages import AuthenticateStage
from allauth.mfa.totp.forms import ActivateTOTPForm, DeactivateTOTPForm
from allauth.socialaccount.forms import DisconnectForm
from allauth.socialaccount.views import SignupView as AllauthSocialSignupView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from inertia import render, share

from common.utils.request import get_request_data

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
            return render(request, "Security/PasswordChange")


# ==============================================================================
# MFA Index — قائمة أجهزة المصادقة الثنائية (2FA)
# ==============================================================================


class MfaListView(LoginRequiredMixin, View):
    """عرض وإدارة المصادقة الثنائية (2FA) عبر Inertia."""

    def get(self, request):
        from apps.users.selectors import is_totp_active

        return render(
            request,
            "Security/MfaList",
            {
                "totp_active": is_totp_active(request.user),
            },
        )


# ==============================================================================
# TOTP Activate — تفعيل المصادقة الثنائية
# ==============================================================================


class TotpActivateView(LoginRequiredMixin, View):
    """تفعيل TOTP/2FA عبر Inertia."""

    def get(self, request):
        from apps.users.selectors import is_totp_active

        # التحقق مما إذا كان مفعلاً بالفعل لتفادي التكرار
        if is_totp_active(request.user):
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
            adapter = get_adapter()
            totp_url = adapter.build_totp_url(request.user, secret)
            totp_svg = adapter.build_totp_svg(totp_url)
            share(request, errors=form.errors.get_json_data())
            return render(
                request,
                "Security/TotpActivate",
                {
                    "totp_svg": totp_svg,
                    "totp_key": secret,
                },
            )


# ==============================================================================
# TOTP Deactivate — تعطيل المصادقة الثنائية
# ==============================================================================


class TotpDeactivateView(LoginRequiredMixin, View):
    """تعطيل TOTP/2FA عبر Inertia."""

    def get_authenticator(self, request):
        from django.http import Http404

        from apps.users.selectors import get_totp_authenticator

        authenticator = get_totp_authenticator(request.user)
        if not authenticator:
            raise Http404("Authenticator not found")
        return authenticator

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
            return render(request, "Security/TotpDeactivate")


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
            return render(request, "Security/MfaAuthenticate")


# ==============================================================================
# Social Connections — إدارة الحسابات الاجتماعية المرتبطة
# ==============================================================================


class SocialConnectionsView(LoginRequiredMixin, View):
    """إدارة الحسابات الاجتماعية المرتبطة عبر Inertia."""

    def get(self, request):
        from apps.users.selectors import list_social_providers, list_user_social_accounts

        accounts = [
            {
                "id": account.id,
                "provider": account.provider,
                "uid": account.uid,
            }
            for account in list_user_social_accounts(request.user)
        ]

        return render(
            request,
            "Security/SocialConnections",
            {
                "accounts": accounts,
                "providers": list_social_providers(),
            },
        )

    def post(self, request):
        data = get_request_data(request)
        form = DisconnectForm(request=request, data=data)

        if form.is_valid():
            form.save()
            return redirect(reverse("auth:social_connections"))
        else:
            from apps.users.selectors import list_social_providers, list_user_social_accounts

            accounts = [
                {
                    "id": account.id,
                    "provider": account.provider,
                    "uid": account.uid,
                }
                for account in list_user_social_accounts(request.user)
            ]
            share(request, errors=form.errors.get_json_data())
            return render(
                request,
                "Security/SocialConnections",
                {
                    "accounts": accounts,
                    "providers": list_social_providers(),
                },
            )


# ==============================================================================
# Social Signup — استكمال التسجيل للحسابات الاجتماعية
# ==============================================================================


class SocialSignupView(AllauthSocialSignupView):
    """استكمال الاشتراك للحسابات الاجتماعية عبر Inertia."""

    def render_to_response(self, context, **response_kwargs):
        provider = context.get("account").provider if context.get("account") else ""
        return render(self.request, "Auth/SocialSignup", {"provider": provider})

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        provider = context.get("account").provider if context.get("account") else ""
        share(self.request, errors=form.errors.get_json_data())
        return render(self.request, "Auth/SocialSignup", {"provider": provider})


# ==============================================================================
# Password Reset — استعادة كلمة المرور عبر البريد (Pure SPA)
# ==============================================================================


class PasswordResetView(AllauthPasswordResetView):
    """صفحة طلب إعادة تعيين كلمة المرور."""

    def render_to_response(self, context, **response_kwargs):
        return render(self.request, "Security/PasswordReset")

    def post(self, request, *args, **kwargs):
        from allauth.account.forms import ResetPasswordForm

        data = get_request_data(request)
        form = ResetPasswordForm(data=data)
        if form.is_valid():
            form.save(request)
            return redirect(reverse("account_reset_password_done"))
        else:
            share(request, errors=form.errors.get_json_data())
            return render(request, "Security/PasswordReset")


class PasswordResetDoneView(AllauthPasswordResetDoneView):
    """صفحة إشعار إرسال بريد استعادة كلمة المرور."""

    def get(self, request, *args, **kwargs):
        return render(request, "Security/PasswordResetDone")


class PasswordResetFromKeyView(AllauthPasswordResetFromKeyView):
    """صفحة كتابة كلمة المرور الجديدة بعد الضغط على الرابط في الإيميل."""

    def dispatch(self, request, uidb36, key, **kwargs):
        is_inertia = (
            request.headers.get("x-inertia") == "true"
            or request.META.get("HTTP_X_INERTIA") == "true"
        )
        if is_inertia:
            if key == self.reset_url_key:
                # allauth stores the real token under "_password_reset_key"
                key = request.session.get("_password_reset_key", "")

            from allauth.account.forms import UserTokenForm

            token_form = UserTokenForm(data={"uidb36": uidb36, "key": key})
            if token_form.is_valid():
                self.reset_user = token_form.reset_user
                self.key = key
                return super(AllauthPasswordResetFromKeyView, self).dispatch(
                    request, uidb36, key, **kwargs
                )
            else:
                self.reset_user = None
                return self.render_to_response({"token_fail": True})

        return super().dispatch(request, uidb36, key, **kwargs)

    def render_to_response(self, context, **response_kwargs):
        token_fail = context.get("token_fail", False)
        return render(self.request, "Security/PasswordResetFromKey", {"token_fail": token_fail})

    def get_form_kwargs(self) -> dict:
        kwargs = super().get_form_kwargs()
        if (
            self.request.content_type and "application/json" in self.request.content_type
        ) or self.request.headers.get("x-inertia") == "true":
            data = get_request_data(self.request)
            kwargs["data"] = {
                "password1": data.get("password"),
                "password2": data.get("password_confirm"),
            }
        return kwargs

    def post(self, request, *args, **kwargs):
        if not getattr(self, "reset_user", None):
            return self.render_to_response({"token_fail": True})

        form = self.get_form()
        if form.is_valid():
            form.save()
            from allauth.account.internal import flows

            resp = flows.password_reset.finalize_password_reset(request, self.reset_user)
            if resp:
                return resp
            return redirect(reverse("account_reset_password_from_key_done"))
        else:
            errors = form.errors.get_json_data()
            mapped_errors = {}
            if "password1" in errors:
                mapped_errors["password"] = errors["password1"]
            if "password2" in errors:
                mapped_errors["password_confirm"] = errors["password2"]
            share(request, errors=mapped_errors)
            return render(request, "Security/PasswordResetFromKey", {"token_fail": False})


class PasswordResetFromKeyDoneView(AllauthPasswordResetFromKeyDoneView):
    """صفحة تأكيد نجاح إعادة تعيين كلمة المرور."""

    def get(self, request, *args, **kwargs):
        return render(request, "Security/PasswordResetFromKeyDone")


class SetLanguageView(View):
    """تغيير لغة التطبيق وتخزينها في الكوكيز والجلسة."""

    def post(self, request):
        data = get_request_data(request)
        lang = data.get("language", "en")
        if lang in ["en", "ar"]:
            from django.conf import settings

            response = redirect(request.META.get("HTTP_REFERER", "/"))
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang)
            if hasattr(request, "session"):
                request.session["_language"] = lang
            return response
        return redirect("/")
