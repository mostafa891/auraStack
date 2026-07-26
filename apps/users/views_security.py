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
# Password Change — Pure SPA
# ==============================================================================


class PasswordChangeView(LoginRequiredMixin, View):
    """Change password view rendered via Inertia."""

    def get(self, request):
        return render(request, "Security/PasswordChange")

    def post(self, request):
        data = get_request_data(request)

        # Map frontend form keys to allauth internal form field names
        mapped_data = {
            "oldpassword": data.get("old_password"),
            "password1": data.get("password"),
            "password2": data.get("password_confirm"),
        }

        form = ChangePasswordForm(user=request.user, data=mapped_data)

        if form.is_valid():
            form.save()
            # Finalize password change, refresh session, and dispatch signals
            from allauth.account.internal.flows.password_change import finalize_password_change

            finalize_password_change(request, form.user)
            return redirect(reverse("profile"))
        else:
            # Map allauth form error keys back to frontend field names
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
# MFA Index — 2FA Devices List
# ==============================================================================


class MfaListView(LoginRequiredMixin, View):
    """Lists multi-factor authentication devices via Inertia."""

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
# TOTP Activate — Enable 2FA
# ==============================================================================


class TotpActivateView(LoginRequiredMixin, View):
    """Activates TOTP/2FA via Inertia."""

    def get(self, request):
        from apps.users.selectors import is_totp_active

        # Prevent duplicate activation if TOTP is already active
        if is_totp_active(request.user):
            return redirect(reverse("auth:mfa_list"))

        # Initialize Allauth form to generate secret automatically
        form = ActivateTOTPForm(user=request.user)
        adapter = get_adapter()
        totp_url = adapter.build_totp_url(request.user, form.secret)
        totp_svg = adapter.build_totp_svg(totp_url)

        # Store secret in session for verification on POST
        request.session["totp_secret"] = form.secret
        request.session["mfa.totp.secret"] = form.secret

        return render(
            request,
            "Security/TotpActivate",
            {
                "totp_svg": totp_svg,
                "totp_key": form.secret,
            },
        )

    def post(self, request):
        secret = request.session.get("totp_secret") or request.session.get("mfa.totp.secret")
        if not secret:
            return redirect(reverse("auth:totp_activate"))

        data = get_request_data(request)
        form = ActivateTOTPForm(user=request.user, data=data)
        form.secret = secret  # Pass saved secret for matching
        request.session["mfa.totp.secret"] = secret

        if form.is_valid():
            from allauth.mfa.totp.internal import flows

            flows.activate_totp(request, form)
            request.session.pop("totp_secret", None)
            request.session.pop("mfa.totp.secret", None)
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
# TOTP Deactivate — Disable 2FA
# ==============================================================================


class TotpDeactivateView(LoginRequiredMixin, View):
    """Deactivates TOTP/2FA via Inertia."""

    def get_authenticator(self, request):
        from django.http import Http404

        from apps.users.selectors import get_totp_authenticator

        authenticator = get_totp_authenticator(request.user)
        if not authenticator:
            raise Http404("Authenticator not found")
        return authenticator

    def get(self, request):
        self.get_authenticator(request)  # Verify existence
        return render(request, "Security/TotpDeactivate")

    def post(self, request):
        authenticator = self.get_authenticator(request)
        data = get_request_data(request)

        # Deactivation form requires authenticator instance
        form = DeactivateTOTPForm(authenticator=authenticator, data=data)

        if form.is_valid():
            from allauth.mfa.totp.internal import flows

            flows.deactivate_totp(request, authenticator)
            return redirect(reverse("auth:mfa_list"))
        else:
            share(request, errors=form.errors.get_json_data())
            return render(request, "Security/TotpDeactivate")


# ==============================================================================
# MFA Authenticate — 2FA Code Verification
# ==============================================================================


@method_decorator(
    login_stage_required(stage=AuthenticateStage.key, redirect_urlname="auth:login"),
    name="dispatch",
)
class MfaAuthenticateView(View):
    """Verifies MFA TOTP code during login via Inertia."""

    def get(self, request):
        return render(request, "Security/MfaAuthenticate")

    def post(self, request):
        stage = request._login_stage
        user = stage.login.user
        data = get_request_data(request)

        form = AuthenticateForm(user=user, data=data)

        if form.is_valid():
            form.save()
            return stage.exit()  # Complete login flow and exit stage
        else:
            share(request, errors=form.errors.get_json_data())
            return render(request, "Security/MfaAuthenticate")


# ==============================================================================
# Social Connections — Manage Connected Accounts
# ==============================================================================


class SocialConnectionsView(LoginRequiredMixin, View):
    """Manages connected social accounts via Inertia."""

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
# Social Signup — Complete Registration for Social Accounts
# ==============================================================================


class SocialSignupView(AllauthSocialSignupView):
    """Completes registration for social account signups via Inertia."""

    def render_to_response(self, context, **response_kwargs):
        provider = context.get("account").provider if context.get("account") else ""
        return render(self.request, "Auth/SocialSignup", {"provider": provider})

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        provider = context.get("account").provider if context.get("account") else ""
        share(self.request, errors=form.errors.get_json_data())
        return render(self.request, "Auth/SocialSignup", {"provider": provider})


# ==============================================================================
# Password Reset — Pure SPA Email Recovery
# ==============================================================================


class PasswordResetView(AllauthPasswordResetView):
    """Password reset request page."""

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
    """Password reset email sent confirmation page."""

    def get(self, request, *args, **kwargs):
        return render(request, "Security/PasswordResetDone")


class PasswordResetFromKeyView(AllauthPasswordResetFromKeyView):
    """Password reset key verification and new password entry page."""

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
    """Password reset success confirmation view."""

    def get(self, request, *args, **kwargs):
        return render(request, "Security/PasswordResetFromKeyDone")


class SetLanguageView(View):
    """Changes application language preference and stores in cookies/session."""

    def post(self, request):
        data = get_request_data(request)
        lang = data.get("language", "en")
        if lang in ["en", "ar"]:
            from django.conf import settings

            response = redirect(request.META.get("HTTP_REFERER", "/"))
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang)
            if hasattr(request, "session"):
                request.session["_language"] = lang
            if hasattr(request, "user") and request.user.is_authenticated:
                request.user.language = lang
                request.user.save(update_fields=["language"])
            return response
        return redirect("/")
