# 🛡️ Django Unfold Admin Panel Guide

AuraFlow features a sleek, responsive administrative panel powered by **django-unfold**, replacing the legacy Django admin styling with a modern dark-mode-first dashboard.

---

## ⚙️ Installed Apps Registration

Because django-unfold overrides admin templates, it **must** be listed before `django.contrib.admin` inside `INSTALLED_APPS` in [base.py](../../core/settings/base.py):

```python
INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "django.contrib.admin",
    ...
]
```

---

## 🛠️ User Admin Configuration (`admin.py`)

AuraFlow customizes the administration model for the custom `CustomUser` user class. The registration is defined in [admin.py](../../apps/users/admin.py):

```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin

from apps.users.forms import CustomUserCreationForm, CustomUserChangeForm
from apps.users.models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin, ModelAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    ...
```

### Key Customizations
1. **Forms**: Connects `CustomUserCreationForm` and `CustomUserChangeForm` so that creation and edit pages work without requiring a username.
2. **List Columns**:
   - Displays custom columns: `email`, `first_name`, `last_name`, `is_staff`, `is_superuser`, `theme`, and `language`.
   - Adds sidebar filters for preferences (theme, language) and permissions.
3. **Fieldsets Customization**:
   Replaces Django's default fieldsets to exclude the `username` field and groups fields cleanly:
   - **Personal Info**: First Name, Last Name, Avatar URL.
   - **Preferences**: Language, Theme, Timezone.
   - **Permissions**: Active state, Staff status, Superuser privileges, Groups, and User permissions.
   - **Important Dates**: Last Login date, Registration Date (`date_joined`).
4. **Creation Layout (`add_fieldsets`)**:
   Provides a simplified form layout for adding users, containing only `email`, `password`, `first_name`, and `last_name`.
