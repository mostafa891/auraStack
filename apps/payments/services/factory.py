from django.conf import settings

from apps.payments.services.stripe import StripeService


class PaymentGatewayFactory:
    @staticmethod
    def get_gateway(provider: str = None):
        provider = provider or getattr(settings, "DEFAULT_PAYMENT_PROVIDER", "STRIPE")
        provider = provider.upper()

        if provider == "STRIPE":
            return StripeService()
        elif provider == "PAYMOB":
            from apps.payments.services.paymob import PaymobService

            return PaymobService()
        elif provider == "LEMONSQUEEZY":
            from apps.payments.services.lemonsqueezy import LemonSqueezyService

            return LemonSqueezyService()
        elif provider == "PAYPAL":
            from apps.payments.services.paypal import PayPalService

            return PayPalService()
        elif provider == "PADDLE":
            from apps.payments.services.paddle import PaddleService

            return PaddleService()

        raise ValueError(f"Unsupported payment provider: {provider}")
