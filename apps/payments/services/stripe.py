import stripe
from django.conf import settings

from apps.payments.interfaces import BasePaymentGateway
from apps.payments.models import PaymentCustomer


class StripeService(BasePaymentGateway):
    def __init__(self):
        stripe.api_key = getattr(settings, "STRIPE_SECRET_KEY", "")

    def create_customer(self, workspace_id: str, email: str) -> str:
        # التحقق من وجود العميل محلياً
        pc = PaymentCustomer.objects.filter(workspace_id=workspace_id, provider="STRIPE").first()
        if pc and pc.customer_id:
            return pc.customer_id

        # إنشاء العميل في Stripe
        customer = stripe.Customer.create(email=email, metadata={"workspace_id": workspace_id})

        # حفظ المعرف محلياً
        PaymentCustomer.objects.update_or_create(
            workspace_id=workspace_id, provider="STRIPE", defaults={"customer_id": customer.id}
        )
        return customer.id

    def create_checkout_session(
        self,
        customer_id: str,
        plan_id: str,
        success_url: str,
        cancel_url: str,
        metadata: dict = None,
    ) -> str:
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            mode="subscription",
            line_items=[
                {
                    "price": plan_id,
                    "quantity": 1,
                }
            ],
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=metadata or {},
            subscription_data={"metadata": metadata or {}},
        )
        return session.url

    def cancel_subscription(self, subscription_id: str) -> bool:
        try:
            stripe.Subscription.delete(subscription_id)
            return True
        except Exception:
            return False

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        endpoint_secret = getattr(settings, "STRIPE_WEBHOOK_SECRET", "")
        if not endpoint_secret:
            return False
        try:
            stripe.Webhook.construct_event(payload, signature, endpoint_secret)
            return True
        except Exception:
            return False

    def parse_event(self, payload: bytes) -> dict:
        import json

        return json.loads(payload)

    def create_portal_session(self, workspace) -> str:
        pc = PaymentCustomer.objects.filter(workspace=workspace, provider="STRIPE").first()
        if not pc or not pc.customer_id:
            owner = workspace.created_by
            customer_id = self.create_customer(str(workspace.id), owner.email if owner else "")
        else:
            customer_id = pc.customer_id

        site_url = getattr(settings, "SITE_URL", "http://localhost:8000")
        session = stripe.billing_portal.Session.create(
            customer=customer_id, return_url=f"{site_url}/profile/"
        )
        return session.url
