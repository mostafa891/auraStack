# Django Ninja API Architecture

AuraStack uses **Django Ninja** for building fast, type-safe, and asynchronous-friendly APIs. Django Ninja leverages Python type hints and Pydantic schemas to automatically parse request payloads, validate data, and generate interactive API documentation.

---

## 📂 Core Concept & Structure

In AuraStack, APIs are split into two security categories defined in [api.py](../../apps/payments/api.py):

### 1. Private API (`private_api`)
* **Endpoint path:** `/api/v1/private/`
* **Authentication:** Uses Django's native session-based authentication (`django_auth`) and cookie-based CSRF protection.
* **Security:** Automatically returns `401 Unauthorized` or `403 Forbidden` if the user is not authenticated or if the CSRF token is invalid.
* **Usage:** Internal frontend component communications (e.g., checkout page requests, workspace configuration shifts).

### 2. Public API (`public_api`)
* **Endpoint path:** `/api/v1/public/`
* **Authentication:** None (open to the public).
* **Security:** Must be secured at the controller level using HMAC signature checks or cryptographic token verification (e.g., Stripe/Paymob webhook routes).
* **Usage:** Receiving webhooks from payment gateways and external third-party service callbacks.

---

## 🛠️ Extending and Creating New APIs

### Step 1: Define a Schema
Use Pydantic `Schema` classes to declare input and output data shapes:
```python
from ninja import Schema

class ProjectCreatePayload(Schema):
    name: str
    description: str | None = None
```

### Step 2: Write the Endpoint Controller
Create your endpoint under the appropriate API instance:
```python
# In apps/your_app/api.py
from ninja import Router
from apps.payments.api import private_api

router = Router()

@router.post("/projects", response={201: dict})
def create_project(request, payload: ProjectCreatePayload):
    # Active workspace and user are automatically accessible
    project = Project.objects.create(
        name=payload.name,
        description=payload.description,
        workspace=request.active_workspace,
        created_by=request.user
    )
    return 201, {"id": str(project.id), "status": "created"}

# Register router to the main API instance in core/urls.py
private_api.add_router("/your-app-path", router)
```

---

## 📖 Interactive Documentation (Swagger)

Django Ninja automatically generates interactive OpenAPI documentation:
* **Swagger UI:** Accessible in development mode at `/api/v1/private/docs` and `/api/v1/public/docs`.
* Mapped schemas, request payloads, and status code variations can be audited and tested directly from the browser.
