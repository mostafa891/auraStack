import datetime

from django.db import transaction
from django.utils.timezone import now

from apps.payments.models import (
    PaymentTransaction,
    ProviderChoices,
    Subscription,
    SubscriptionStatusChoices,
)
from apps.payments.services.factory import PaymentGatewayFactory


def process_stripe_webhook(payload: bytes, sig_header: str):
    stripe_service = PaymentGatewayFactory.get_gateway("STRIPE")
    if not stripe_service.verify_webhook_signature(payload, sig_header):
        raise ValueError("Invalid Stripe signature")

    event = stripe_service.parse_event(payload)
    event_type = event.get("type")

    if event_type == "checkout.session.completed":
        session = event["data"]["object"]
        workspace_id = session.get("metadata", {}).get("workspace_id")
        if not workspace_id:
            return

        subscription_id = session.get("subscription")

        with transaction.atomic():
            sub, created = Subscription.objects.select_for_update().get_or_create(
                workspace_id=workspace_id,
                defaults={
                    "provider": ProviderChoices.STRIPE,
                    "subscription_id": subscription_id,
                    "plan_id": "pro",
                    "status": SubscriptionStatusChoices.ACTIVE,
                    "current_period_end": now() + datetime.timedelta(days=30),
                },
            )
            if not created:
                sub.provider = ProviderChoices.STRIPE
                sub.subscription_id = subscription_id
                sub.plan_id = "pro"
                sub.status = SubscriptionStatusChoices.ACTIVE
                sub.current_period_end = now() + datetime.timedelta(days=30)
                sub.save()

            # تسجيل الحركة المالية
            PaymentTransaction.objects.update_or_create(
                transaction_id=session.get("id"),
                defaults={
                    "workspace_id": workspace_id,
                    "provider": ProviderChoices.STRIPE,
                    "amount": session.get("amount_total", 0) / 100.0,
                    "currency": session.get("currency", "usd").upper(),
                    "status": "succeeded",
                },
            )

    elif event_type in ["customer.subscription.updated", "customer.subscription.deleted"]:
        stripe_sub = event["data"]["object"]
        subscription_id = stripe_sub.get("id")

        stripe_status = stripe_sub.get("status")
        status_map = {
            "active": SubscriptionStatusChoices.ACTIVE,
            "trialing": SubscriptionStatusChoices.TRIALLING,
            "past_due": SubscriptionStatusChoices.PAST_DUE,
            "canceled": SubscriptionStatusChoices.CANCELED,
            "unpaid": SubscriptionStatusChoices.UNPAID,
        }
        mapped_status = status_map.get(stripe_status, SubscriptionStatusChoices.INACTIVE)
        period_end = datetime.datetime.fromtimestamp(
            stripe_sub.get("current_period_end"), tz=datetime.UTC
        )
        cancel_at_period_end = stripe_sub.get("cancel_at_period_end", False)

        with transaction.atomic():
            sub = (
                Subscription.objects.select_for_update()
                .filter(subscription_id=subscription_id, provider=ProviderChoices.STRIPE)
                .first()
            )
            if sub:
                sub.status = mapped_status
                sub.current_period_end = period_end
                sub.cancel_at_period_end = cancel_at_period_end
                sub.save()


def process_paymob_webhook(payload: dict, params: dict):
    # Stub لـ Paymob
    pass
