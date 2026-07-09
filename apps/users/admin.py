from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin

from apps.users.forms import CustomUserChangeForm, CustomUserCreationForm
from apps.users.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin, ModelAdmin):
    """تخصيص لوحة إدارة المستخدم المخصص وتزيينها بسمة Unfold الراقية."""

    add_form = CustomUserCreationForm
    form = CustomUserChangeForm

    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_superuser",
        "theme",
        "language",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "theme", "language")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)

    # إعادة كتابة مجموعات الحقول لإقصاء اسم المستخدم (username) تماماً
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "avatar_url")}),
        (
            _("Preferences"),
            {"fields": ("language", "theme", "timezone")},
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    # فورم إضافة مستخدم جديد في لوحة الإدارة
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password", "first_name", "last_name"),
            },
        ),
    )
