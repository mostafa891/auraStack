from typing import Any

from django import forms
from django.contrib.auth.forms import (
    UserChangeForm as BaseUserChangeForm,
)
from django.contrib.auth.forms import (
    UserCreationForm as BaseUserCreationForm,
)
from django.utils.translation import gettext_lazy as _

from apps.users.models import CustomUser
from common.utils.email import normalize_email


class AuraLoginForm(forms.Form):
    """نموذج فحص وتطهير مدخلات تسجيل الدخول لمنصة AuraFlow."""

    email = forms.EmailField(
        required=True,
        error_messages={"required": _("Email address is required.")},
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput,
        error_messages={"required": _("Password is required.")},
    )

    def clean_email(self) -> str:
        return normalize_email(self.cleaned_data["email"])


class AuraRegisterForm(forms.Form):
    """نموذج فحص وتطهير مدخلات حساب جديد دون التدخل في شروط العمل."""

    email = forms.EmailField(
        required=True,
        error_messages={"required": _("Email address is required.")},
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput,
        error_messages={"required": _("Password must be at least 8 characters.")},
    )
    password_confirm = forms.CharField(
        required=True,
        widget=forms.PasswordInput,
        error_messages={"required": _("Password confirmation is required.")},
    )

    def clean_email(self) -> str:
        return normalize_email(self.cleaned_data["email"])

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error("password_confirm", _("Passwords do not match."))
        return cleaned_data


class ProfileUpdateForm(forms.ModelForm):
    """نموذج تحديث التفضيلات الشخصية للمستخدم (اللغة، المظهر، المنطقة الزمنية)."""

    class Meta:
        model = CustomUser
        fields = ["language", "theme", "timezone"]


class CustomUserCreationForm(BaseUserCreationForm):
    class Meta(BaseUserCreationForm.Meta):
        model = CustomUser
        fields = ("email",)


class CustomUserChangeForm(BaseUserChangeForm):
    class Meta(BaseUserChangeForm.Meta):
        model = CustomUser
        fields = "__all__"
