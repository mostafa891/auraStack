# apps/users/adapters/allauth.py
from allauth.account.adapter import DefaultAccountAdapter, get_adapter
from allauth.account.forms import LoginForm
from allauth.account.utils import complete_signup
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import HttpRequest

from common.results import AuthErrorCode, ServiceResult


class CustomAccountAdapter(DefaultAccountAdapter):
    def is_ajax(self, request: HttpRequest) -> bool:
        if request.headers.get("x-inertia") or request.META.get("HTTP_X_INERTIA"):
            return False
        return super().is_ajax(request)


class AllauthAdapter:
    """Adapter bridging django-allauth internal services and APIs."""

    @staticmethod
    def authenticate_user(
        request: HttpRequest, email: str, password: str, remember: bool = False
    ) -> ServiceResult:
        form = LoginForm(
            request=request, data={"login": email, "password": password, "remember": remember}
        )

        if not form.is_valid():
            errors = form.errors.get_json_data()
            error_code = AuthErrorCode.INVALID_CREDENTIALS
            if form.errors.as_data().get("__all__"):
                for error in form.errors.as_data()["__all__"]:
                    if error.code == "account_inactive":
                        error_code = AuthErrorCode.ACCOUNT_INACTIVE
            return ServiceResult(success=False, errors=errors, code=error_code)

        response = form.login(request)
        return ServiceResult(success=True, data=response)

    @staticmethod
    def register_user(request: HttpRequest, email: str, password: str) -> ServiceResult:
        """Registers a new user using the official allauth adapter API."""
        adapter = get_adapter(request)
        user = adapter.new_user(request)
        user.email = email

        try:
            # Enforce Django and allauth password validation policies
            adapter.clean_password(password, user)
            user.set_password(password)

            # Save user instance - raises IntegrityError if email is duplicated
            user.save()

            # Initialize user email in Allauth tables to create EmailAddress record
            from allauth.account.utils import setup_user_email

            setup_user_email(request, user, [])

            # Complete allauth signup lifecycle (dispatch signals, trigger emails)
            complete_signup(
                request=request,
                user=user,
                email_verification="none",  # Governed by default settings
                success_url="/",
            )
            return ServiceResult(success=True, data=user)

        except ValidationError as e:
            # Validation error raised from clean_password pertains to password policy
            errors = e.message_dict if hasattr(e, "error_dict") else {"password": e.messages}
            return ServiceResult(
                success=False, errors=errors, code=AuthErrorCode.INVALID_CREDENTIALS
            )
        except IntegrityError:
            # Catch database level unique constraint race condition
            return ServiceResult(success=False, code=AuthErrorCode.EMAIL_ALREADY_EXISTS)
