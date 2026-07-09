# 🔗 Inertia-Django Architecture Guide

Inertia.js allows AuraFlow to operate as a Single Page Application (SPA) using server-side controllers and routes without requiring a separate REST or GraphQL API server.

---

## ⚙️ Core Configuration

Registered in `base.py`:
- **Middleware**: `inertia.middleware.InertiaMiddleware` intercepts client requests and formats JSON/HTML responses dynamically.
- **CSRF Token Compatibility**: Configured to work seamlessly with Axios (Inertia's internal HTTP client):
  ```python
  CSRF_HEADER_NAME = "HTTP_X_XSRF_TOKEN"
  CSRF_COOKIE_NAME = "XSRF-TOKEN"
  ```
- **Root Layout**: `INERTIA_LAYOUT = "base.html"`. The root template is located at [base.html](file:///a:/auraflow/templates/base.html) and contains the `{% block inertia %}` tag where the Vue app mounts.

---

## 🔄 Shared Data (Shared Props)

Global variables are shared automatically across all Vue 3 pages through Django middleware.

### User Context
In [middleware.py](file:///a:/auraflow/common/middleware.py), user attributes are shared with every request:
```python
share(
    request,
    auth={
        "user": {
            "id": str(request.user.id),
            "email": request.user.email,
            "avatar_url": request.user.avatar_url,
            "language": request.user.language,
            "theme": request.user.theme,
            "timezone": request.user.timezone,
        }
    }
)
```

### Form & Validation Errors
Validation errors from Django Forms are shared via views (e.g. `LoginView`, `RegisterView`):
```python
share(request, errors=form.errors.get_json_data())
```
These are caught in Vue using the custom `useFormErrors` composable.

---

## 🚀 How to Add a New Inertia Page (Step-by-Step)

To add a new page (e.g. "Pricing Dashboard") to AuraFlow:

### Step 1: Create the Vue Component
Create `frontend/src/pages/Dashboard/Pricing.vue`:
```html
<script setup lang="ts">
import { Link } from "@inertiajs/vue3";
defineProps<{ plan_name: string }>();
</script>

<template>
  <div class="p-8">
    <h1>Pricing Plan: {{ plan_name }}</h1>
    <Link href="/profile/" class="text-indigo-600">Back to Profile</Link>
  </div>
</template>
```

### Step 2: Write the Django View
Create a View class in `apps/users/views.py` (or your specific app's views):
```python
from inertia import render
from django.views import View

class PricingView(View):
    def get(self, request):
        return render(request, "Dashboard/Pricing", {
            "plan_name": "Premium Enterprise"
        })
```

### Step 3: Register the URL Route
Add the view to `urls.py`:
```python
from django.urls import path
from .views import PricingView

urlpatterns = [
    path("pricing/", PricingView.as_view(), name="pricing"),
]
```
Now, navigating to `/pricing/` will render the component as an SPA page without full-page reloads!
