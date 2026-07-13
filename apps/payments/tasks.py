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
        # استخراج plan_id من الـ metadata أو الـ line_items — مع fallback آمن
        plan_id = (
            session.get("metadata", {}).get("plan_id")
            or "pro"  # fallback للإصدارات القديمة التي لا تُرسل plan_id في metadata
        )

        with transaction.atomic():
            sub, created = Subscription.objects.select_for_update().get_or_create(
                workspace_id=workspace_id,
                defaults={
                    "provider": ProviderChoices.STRIPE,
                    "subscription_id": subscription_id,
                    "plan_id": plan_id,
                    "status": SubscriptionStatusChoices.ACTIVE,
                    "current_period_end": now() + datetime.timedelta(days=30),
                },
            )
            if not created:
                sub.provider = ProviderChoices.STRIPE
                sub.subscription_id = subscription_id
                sub.plan_id = plan_id
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
    """
    معالجة webhooks الواردة من Paymob.
    Paymob يُرسل بيانات الدفع عبر GET params + POST body.
    """
    import logging

    logger = logging.getLogger(__name__)

    obj = payload.get("obj", {})
    success = obj.get("success", False)
    pending = obj.get("pending", True)

    if success and not pending:
        # استخراج workspace_id من merchant_order_id
        order = obj.get("order", {})
        workspace_id = order.get("merchant_order_id")
        if not workspace_id:
            logger.warning("Paymob webhook: missing merchant_order_id in payload")
            return

        amount_cents = obj.get("amount_cents", 0)
        transaction_id = str(obj.get("id", ""))

        with transaction.atomic():
            sub, created = Subscription.objects.select_for_update().get_or_create(
                workspace_id=workspace_id,
                defaults={
                    "provider": ProviderChoices.PAYMOB,
                    "plan_id": "pro",
                    "status": SubscriptionStatusChoices.ACTIVE,
                    "current_period_end": now() + datetime.timedelta(days=30),
                },
            )
            if not created:
                sub.status = SubscriptionStatusChoices.ACTIVE
                sub.current_period_end = now() + datetime.timedelta(days=30)
                sub.save()

            PaymentTransaction.objects.update_or_create(
                transaction_id=transaction_id,
                defaults={
                    "workspace_id": workspace_id,
                    "provider": ProviderChoices.PAYMOB,
                    "amount": amount_cents / 100.0,
                    "currency": obj.get("currency", "EGP").upper(),
                    "status": "succeeded",
                },
            )
        logger.info(f"Paymob payment processed for workspace {workspace_id}")
    else:
        logger.info(f"Paymob webhook received — not a successful payment (success={success})")


def process_lemonsqueezy_webhook(payload: bytes, signature: str):
    """معالجة webhooks الواردة من LemonSqueezy."""
    import json
    import logging

    logger = logging.getLogger(__name__)

    from apps.payments.services.factory import PaymentGatewayFactory

    ls_service = PaymentGatewayFactory.get_gateway("LEMONSQUEEZY")

    if not ls_service.verify_webhook_signature(payload, signature):
        raise ValueError("Invalid LemonSqueezy webhook signature")

    event = json.loads(payload.decode("utf-8"))
    event_name = event.get("meta", {}).get("event_name", "")
    data = event.get("data", {})
    attrs = data.get("attributes", {})

    workspace_id = event.get("meta", {}).get("custom_data", {}).get("workspace_id") or attrs.get(
        "custom_data", {}
    ).get("workspace_id")
    if not workspace_id:
        logger.warning(f"LemonSqueezy webhook: no workspace_id in event '{event_name}'")
        return

    if event_name == "order_created":
        with transaction.atomic():
            sub, _ = Subscription.objects.select_for_update().get_or_create(
                workspace_id=workspace_id,
                defaults={
                    "provider": ProviderChoices.LEMONSQUEEZY,
                    "subscription_id": str(data.get("id", "")),
                    "plan_id": "pro",
                    "status": SubscriptionStatusChoices.ACTIVE,
                    "current_period_end": now() + datetime.timedelta(days=30),
                },
            )
            PaymentTransaction.objects.update_or_create(
                transaction_id=str(data.get("id", "")),
                defaults={
                    "workspace_id": workspace_id,
                    "provider": ProviderChoices.LEMONSQUEEZY,
                    "amount": attrs.get("total", 0) / 100.0,
                    "currency": attrs.get("currency", "USD").upper(),
                    "status": "succeeded",
                },
            )
    elif event_name in ["subscription_expired", "subscription_cancelled"]:
        Subscription.objects.filter(
            workspace_id=workspace_id, provider=ProviderChoices.LEMONSQUEEZY
        ).update(status=SubscriptionStatusChoices.CANCELED)

    logger.info(f"LemonSqueezy webhook '{event_name}' processed for workspace {workspace_id}")


def process_paddle_webhook(payload: bytes, signature: str):
    """معالجة webhooks الواردة من Paddle Billing."""
    import json
    import logging

    logger = logging.getLogger(__name__)

    from apps.payments.services.factory import PaymentGatewayFactory

    paddle_service = PaymentGatewayFactory.get_gateway("PADDLE")

    if not paddle_service.verify_webhook_signature(payload, signature):
        raise ValueError("Invalid Paddle webhook signature")

    event = json.loads(payload.decode("utf-8"))
    event_type = event.get("event_type", "")
    data = event.get("data", {})
    custom_data = data.get("custom_data", {})
    workspace_id = custom_data.get("workspace_id")

    if not workspace_id:
        logger.warning(f"Paddle webhook: no workspace_id in event '{event_type}'")
        return

    if event_type == "transaction.completed":
        with transaction.atomic():
            sub, _ = Subscription.objects.select_for_update().get_or_create(
                workspace_id=workspace_id,
                defaults={
                    "provider": ProviderChoices.PADDLE,
                    "subscription_id": data.get("subscription_id", ""),
                    "plan_id": "pro",
                    "status": SubscriptionStatusChoices.ACTIVE,
                    "current_period_end": now() + datetime.timedelta(days=30),
                },
            )
            details = data.get("details", {}).get("totals", {})
            PaymentTransaction.objects.update_or_create(
                transaction_id=data.get("id", ""),
                defaults={
                    "workspace_id": workspace_id,
                    "provider": ProviderChoices.PADDLE,
                    "amount": float(details.get("total", 0)) / 100.0,
                    "currency": data.get("currency_code", "USD").upper(),
                    "status": "succeeded",
                },
            )
    elif event_type == "subscription.canceled":
        Subscription.objects.filter(
            workspace_id=workspace_id, provider=ProviderChoices.PADDLE
        ).update(status=SubscriptionStatusChoices.CANCELED)

    logger.info(f"Paddle webhook '{event_type}' processed for workspace {workspace_id}")


def process_paypal_webhook(payload: bytes, signature: str):
    """معالجة webhooks الواردة من PayPal."""
    import json
    import logging

    logger = logging.getLogger(__name__)

    from apps.payments.services.factory import PaymentGatewayFactory

    paypal_service = PaymentGatewayFactory.get_gateway("PAYPAL")

    if not paypal_service.verify_webhook_signature(payload, signature):
        raise ValueError("Invalid PayPal webhook signature")

    event = json.loads(payload.decode("utf-8"))
    event_type = event.get("event_type", "")
    resource = event.get("resource", {})
    workspace_id = resource.get("custom_id")

    if not workspace_id:
        logger.warning(f"PayPal webhook: no workspace_id (custom_id) in event '{event_type}'")
        return

    if event_type == "BILLING.SUBSCRIPTION.ACTIVATED":
        with transaction.atomic():
            sub, _ = Subscription.objects.select_for_update().get_or_create(
                workspace_id=workspace_id,
                defaults={
                    "provider": ProviderChoices.PAYPAL,
                    "subscription_id": resource.get("id", ""),
                    "plan_id": "pro",
                    "status": SubscriptionStatusChoices.ACTIVE,
                    "current_period_end": now() + datetime.timedelta(days=30),
                },
            )
    elif event_type == "BILLING.SUBSCRIPTION.CANCELLED":
        Subscription.objects.filter(
            workspace_id=workspace_id, provider=ProviderChoices.PAYPAL
        ).update(status=SubscriptionStatusChoices.CANCELED)

    logger.info(f"PayPal webhook '{event_type}' processed for workspace {workspace_id}")
