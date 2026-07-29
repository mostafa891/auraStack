import json

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django_q.tasks import async_task
from ninja import NinjaAPI, Schema
from ninja.security import django_auth

from apps.payments.services.factory import PaymentGatewayFactory
from apps.teams.models import Workspace, WorkspaceMember
from apps.teams.selectors import get_workspace_membership

# User billing API (protected by session auth and CSRF protection)
private_api = NinjaAPI(auth=django_auth, version="1.0.0", urls_namespace="payments_private")

# Public Webhook & System Health API endpoints
public_api = NinjaAPI(version="1.0.0", urls_namespace="payments_public")


@public_api.get("/health")
def health_check(request: HttpRequest):
    """System health check endpoint for uptime monitoring and container probes."""
    from django.db import connection
    from django.http import JsonResponse

    db_ok = True
    try:
        connection.ensure_connection()
    except Exception:
        db_ok = False

    status_code = 200 if db_ok else 503
    return JsonResponse(
        {
            "status": "healthy" if db_ok else "unhealthy",
            "database": "ok" if db_ok else "error",
            "service": "auraStack",
            "version": "1.0.0",
        },
        status=status_code,
    )


class CheckoutPayload(Schema):
    workspace_id: str
    plan_id: str
    gateway: str


@private_api.post("/billing/checkout")
def create_checkout_session(request: HttpRequest, payload: CheckoutPayload):
    workspace = get_object_or_404(Workspace, id=payload.workspace_id)

    # Protect against BOLA / IDOR vulnerabilities
    membership = get_workspace_membership(workspace, request.user)
    if not membership or membership.role not in [
        WorkspaceMember.RoleChoices.OWNER,
        WorkspaceMember.RoleChoices.ADMIN,
    ]:
        return HttpResponse("Access denied. Owners/Admins only.", status=403)

    gateway_service = PaymentGatewayFactory.get_gateway(payload.gateway)

    # Retrieve or register gateway customer ID
    customer_id = gateway_service.create_customer(
        workspace_id=str(workspace.id), email=request.user.email
    )

    from django.conf import settings

    site_url = getattr(settings, "SITE_URL", "http://localhost:8000")
    success_url = f"{site_url}/profile/?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{site_url}/profile/"

    # Generate gateway checkout URL
    checkout_url = gateway_service.create_checkout_session(
        customer_id=customer_id,
        plan_id=payload.plan_id,
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={"workspace_id": str(workspace.id)},
    )
    return {"checkout_url": checkout_url}


@public_api.post("/billing/webhooks/stripe")
def stripe_webhook(request: HttpRequest):
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    if not sig_header:
        return HttpResponse("Missing signature", status=400)

    # Offload webhook processing to background Q2 task
    async_task(
        "apps.payments.tasks.process_stripe_webhook",
        payload=request.body,
        sig_header=sig_header,
    )
    return HttpResponse(status=200)


@public_api.post("/billing/webhooks/paymob")
def paymob_webhook(request: HttpRequest):
    try:
        data = json.loads(request.body.decode("utf-8")) if request.body else {}
    except Exception:
        data = {}

    params = request.GET.dict()

    async_task(
        "apps.payments.tasks.process_paymob_webhook",
        payload=data,
        params=params,
        raw_payload=request.body,
    )
    return HttpResponse(status=200)


@public_api.post("/billing/webhooks/lemonsqueezy")
def lemonsqueezy_webhook(request: HttpRequest):
    signature = request.META.get("HTTP_X_SIGNATURE")
    if not signature:
        return HttpResponse("Missing signature", status=400)

    async_task(
        "apps.payments.tasks.process_lemonsqueezy_webhook",
        payload=request.body,
        signature=signature,
    )
    return HttpResponse(status=200)


@public_api.post("/billing/webhooks/paypal")
def paypal_webhook(request: HttpRequest):
    headers = {
        "PAYPAL-AUTH-ALGO": request.META.get("HTTP_PAYPAL_AUTH_ALGO", ""),
        "PAYPAL-TRANSMISSION-ID": request.META.get("HTTP_PAYPAL_TRANSMISSION_ID", ""),
        "PAYPAL-CERT-URL": request.META.get("HTTP_PAYPAL_CERT_URL", ""),
        "PAYPAL-TRANSMISSION-SIG": request.META.get("HTTP_PAYPAL_TRANSMISSION_SIG", ""),
        "PAYPAL-TRANSMISSION-TIME": request.META.get("HTTP_PAYPAL_TRANSMISSION_TIME", ""),
    }

    async_task(
        "apps.payments.tasks.process_paypal_webhook",
        payload=request.body,
        headers=headers,
    )
    return HttpResponse(status=200)


@public_api.post("/billing/webhooks/paddle")
def paddle_webhook(request: HttpRequest):
    signature = request.META.get("HTTP_PADDLE_SIGNATURE", "")
    if not signature:
        return HttpResponse("Missing signature", status=400)

    async_task(
        "apps.payments.tasks.process_paddle_webhook",
        payload=request.body,
        signature=signature,
    )
    return HttpResponse(status=200)
