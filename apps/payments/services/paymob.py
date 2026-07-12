from apps.payments.interfaces import BasePaymentGateway


class PaymobService(BasePaymentGateway):
    def create_customer(self, workspace_id: str, email: str) -> str:
        return "paymob_customer_stub"

    def create_checkout_session(
        self,
        customer_id: str,
        plan_id: str,
        success_url: str,
        cancel_url: str,
        metadata: dict = None,
    ) -> str:
        return "https://paymob.com/stub-checkout"

    def cancel_subscription(self, subscription_id: str) -> bool:
        return True

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        return True
