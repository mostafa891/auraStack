import hashlib
import hmac
import json
import logging
import urllib.request

from django.conf import settings

from apps.payments.interfaces import BasePaymentGateway

logger = logging.getLogger(__name__)


class PaddleService(BasePaymentGateway):
    """
    تطبيق كامل لبوابة الدفع Paddle Billing (v2).

    المتغيرات المطلوبة في .env:
        PADDLE_API_KEY        — مفتاح API من لوحة تحكم Paddle
        PADDLE_WEBHOOK_SECRET — مفتاح التحقق من webhooks
        PADDLE_ENVIRONMENT    — 'sandbox' أو 'production'
    """

    def __init__(self):
        self.api_key = getattr(settings, "PADDLE_API_KEY", "")
        self.webhook_secret = getattr(settings, "PADDLE_WEBHOOK_SECRET", "")
        env = getattr(settings, "PADDLE_ENVIRONMENT", "sandbox")
        self.base_url = (
            "https://api.paddle.com" if env == "production" else "https://sandbox-api.paddle.com"
        )

    def _paddle_request(self, method: str, endpoint: str, payload: dict = None) -> dict:
        """دالة مساعدة لإرسال طلبات لـ Paddle API."""
        url = f"{self.base_url}{endpoint}"
        data = json.dumps(payload).encode("utf-8") if payload else None
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method=method,
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def create_customer(self, workspace_id: str, email: str) -> str:
        """إنشاء عميل في Paddle."""
        if not self.api_key:
            raise ValueError("PADDLE_API_KEY is not configured")
        try:
            response = self._paddle_request(
                "POST",
                "/customers",
                {"email": email, "custom_data": {"workspace_id": workspace_id}},
            )
            return response["data"]["id"]
        except Exception as e:
            logger.error(f"Paddle create_customer error: {e}")
            return workspace_id

    def create_checkout_session(
        self,
        customer_id: str,
        plan_id: str,
        success_url: str,
        cancel_url: str,
        metadata: dict = None,
    ) -> str:
        """إنشاء رابط Paddle Checkout."""
        if not self.api_key:
            raise ValueError("PADDLE_API_KEY is not configured")
        try:
            response = self._paddle_request(
                "POST",
                "/transactions",
                {
                    "items": [{"price_id": plan_id, "quantity": 1}],
                    "customer_id": customer_id,
                    "checkout": {"url": success_url},
                    "custom_data": metadata or {},
                },
            )
            checkout = response["data"].get("checkout", {})
            return checkout.get("url", success_url)
        except Exception as e:
            logger.error(f"Paddle create_checkout_session error: {e}")
            raise

    def cancel_subscription(self, subscription_id: str) -> bool:
        """إلغاء اشتراك Paddle."""
        if not self.api_key:
            return False
        try:
            self._paddle_request(
                "POST",
                f"/subscriptions/{subscription_id}/cancel",
                {"effective_from": "next_billing_period"},
            )
            return True
        except Exception as e:
            logger.error(f"Paddle cancel_subscription error: {e}")
            return False

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """التحقق من HMAC-SHA256 لـ Paddle webhooks."""
        if not self.webhook_secret:
            logger.error("PADDLE_WEBHOOK_SECRET is not set")
            return False
        try:
            # Paddle يُرسل: ts=TIMESTAMP;h1=SIGNATURE
            parts = dict(item.split("=", 1) for item in signature.split(";"))
            ts = parts.get("ts", "")
            h1 = parts.get("h1", "")
            signed_payload = f"{ts}:{payload.decode('utf-8')}"
            expected = hmac.new(
                self.webhook_secret.encode("utf-8"),
                signed_payload.encode("utf-8"),
                hashlib.sha256,
            ).hexdigest()
            return hmac.compare_digest(expected, h1)
        except Exception as e:
            logger.error(f"Paddle webhook verification error: {e}")
            return False
