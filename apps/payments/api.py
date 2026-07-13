import json

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django_q.tasks import async_task
from ninja import NinjaAPI, Schema
from ninja.security import django_auth

from apps.payments.services.factory import PaymentGatewayFactory
from apps.teams.models import Workspace, WorkspaceMember
from apps.teams.selectors import get_workspace_membership

# الـ API الخاص بمعاملات المستخدمين (محمي بـ CSRF ومصادقة الجلسة أوتوماتيكياً بواسطة django_auth)
private_api = NinjaAPI(auth=django_auth, version="1.0.0", urls_namespace="payments_private")

# الـ API المفتوح للـ Webhooks
public_api = NinjaAPI(version="1.0.0", urls_namespace="payments_public")


class CheckoutPayload(Schema):
    workspace_id: str
    plan_id: str
    gateway: str


@private_api.post("/billing/checkout")
def create_checkout_session(request: HttpRequest, payload: CheckoutPayload):
    workspace = get_object_or_404(Workspace, id=payload.workspace_id)

    # التحقق ضد ثغرات BOLA/IDOR
    membership = get_workspace_membership(workspace, request.user)
    if not membership or membership.role not in [
        WorkspaceMember.RoleChoices.OWNER,
        WorkspaceMember.RoleChoices.ADMIN,
    ]:
        return HttpResponse("Access denied. Owners/Admins only.", status=403)

    gateway_service = PaymentGatewayFactory.get_gateway(payload.gateway)

    # جلب أو إنشاء معرّف العميل لدى البوابة
    customer_id = gateway_service.create_customer(
        workspace_id=str(workspace.id), email=request.user.email
    )

    from django.conf import settings

    site_url = getattr(settings, "SITE_URL", "http://localhost:8000")
    success_url = f"{site_url}/profile/?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{site_url}/profile/"

    # توليد الجلسة ورابط الدفع
    checkout_url = gateway_service.create_checkout_session(
        customer_id=customer_id,
        plan_id=payload.plan_id,
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={"workspace_id": str(workspace.id)},
    )
    return {"checkout_url": checkout_url}


@private_api.get("/billing/portal/{workspace_id}")
def create_billing_portal(request: HttpRequest, workspace_id: str):
    workspace = get_object_or_404(Workspace, id=workspace_id)

    membership = get_workspace_membership(workspace, request.user)
    if not membership or membership.role not in [
        WorkspaceMember.RoleChoices.OWNER,
        WorkspaceMember.RoleChoices.ADMIN,
    ]:
        return HttpResponse("Access denied.", status=403)

    gateway_service = PaymentGatewayFactory.get_gateway("STRIPE")
    portal_url = gateway_service.create_portal_session(workspace)
    return {"portal_url": portal_url}


@public_api.post("/billing/webhooks/stripe")
def stripe_webhook(request: HttpRequest):
    sig_header = request.headers.get("stripe-signature")
    if not sig_header:
        return HttpResponse("Missing signature", status=400)

    # تفويض المعالجة لـ Q2 في الخلفية
    async_task("apps.payments.tasks.process_stripe_webhook", request.body, sig_header)
    return HttpResponse(status=200)


@public_api.post("/billing/webhooks/paymob")
def paymob_webhook(request: HttpRequest):
    try:
        body = json.loads(request.body.decode("utf-8"))
    except Exception:
        body = {}
    async_task("apps.payments.tasks.process_paymob_webhook", body, dict(request.GET.items()))
    return HttpResponse(status=200)


@public_api.post("/billing/webhooks/lemonsqueezy")
def lemonsqueezy_webhook(request: HttpRequest):
    sig_header = request.headers.get("X-Signature")
    if not sig_header:
        return HttpResponse("Missing signature", status=400)
    async_task("apps.payments.tasks.process_lemonsqueezy_webhook", request.body, sig_header)
    return HttpResponse(status=200)


@public_api.post("/billing/webhooks/paddle")
def paddle_webhook(request: HttpRequest):
    sig_header = request.headers.get("Paddle-Signature")
    if not sig_header:
        return HttpResponse("Missing Paddle-Signature header", status=400)
    async_task("apps.payments.tasks.process_paddle_webhook", request.body, sig_header)
    return HttpResponse(status=200)


@public_api.post("/billing/webhooks/paypal")
def paypal_webhook(request: HttpRequest):
    sig_header = request.headers.get("Paypal-Transmission-Sig", "")
    async_task("apps.payments.tasks.process_paypal_webhook", request.body, sig_header)
    return HttpResponse(status=200)
