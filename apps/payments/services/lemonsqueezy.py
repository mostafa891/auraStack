import hashlib
import hmac
import json
import logging
import urllib.request

from django.conf import settings

from apps.payments.interfaces import BasePaymentGateway

logger = logging.getLogger(__name__)

LEMONSQUEEZY_BASE_URL = "https://api.lemonsqueezy.com/v1"


def _ls_request(method: str, endpoint: str, payload: dict = None, api_key: str = "") -> dict:
    """دالة مساعدة لإرسال طلبات لـ LemonSqueezy API."""
    url = f"{LEMONSQUEEZY_BASE_URL}{endpoint}"
    data = json.dumps(payload).encode("utf-8") if payload else None
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/vnd.api+json",
            "Accept": "application/vnd.api+json",
        },
        method=method,
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


class LemonSqueezyService(BasePaymentGateway):
    """
    تطبيق كامل لبوابة الدفع LemonSqueezy.

    المتغيرات المطلوبة في .env:
        LEMONSQUEEZY_API_KEY       — مفتاح API من لوحة تحكم LemonSqueezy
        LEMONSQUEEZY_STORE_ID      — معرّف المتجر
        LEMONSQUEEZY_WEBHOOK_SECRET — مفتاح التحقق من webhooks
    """

    def __init__(self):
        self.api_key = getattr(settings, "LEMONSQUEEZY_API_KEY", "")
        self.store_id = getattr(settings, "LEMONSQUEEZY_STORE_ID", "")
        self.webhook_secret = getattr(settings, "LEMONSQUEEZY_WEBHOOK_SECRET", "")

    def create_customer(self, workspace_id: str, email: str) -> str:
        """إنشاء أو جلب عميل في LemonSqueezy."""
        if not self.api_key:
            raise ValueError("LEMONSQUEEZY_API_KEY is not configured")
        try:
            payload = {
                "data": {
                    "type": "customers",
                    "attributes": {"name": f"Workspace {workspace_id[:8]}", "email": email},
                    "relationships": {
                        "store": {"data": {"type": "stores", "id": str(self.store_id)}}
                    },
                }
            }
            response = _ls_request("POST", "/customers", payload, self.api_key)
            return str(response["data"]["id"])
        except Exception as e:
            logger.error(f"LemonSqueezy create_customer error: {e}")
            return workspace_id  # fallback

    def create_checkout_session(
        self,
        customer_id: str,
        plan_id: str,
        success_url: str,
        cancel_url: str,
        metadata: dict = None,
    ) -> str:
        """إنشاء جلسة Checkout عبر LemonSqueezy."""
        if not self.api_key or not self.store_id:
            raise ValueError(
                "LemonSqueezy is not configured. Set LEMONSQUEEZY_API_KEY and LEMONSQUEEZY_STORE_ID"
            )
        payload = {
            "data": {
                "type": "checkouts",
                "attributes": {
                    "checkout_options": {
                        "success_url": success_url,
                    },
                    "checkout_data": {
                        "custom": metadata or {},
                    },
                    "product_options": {
                        "redirect_url": success_url,
                    },
                },
                "relationships": {
                    "store": {"data": {"type": "stores", "id": str(self.store_id)}},
                    "variant": {"data": {"type": "variants", "id": str(plan_id)}},
                },
            }
        }
        response = _ls_request("POST", "/checkouts", payload, self.api_key)
        return response["data"]["attributes"]["url"]

    def cancel_subscription(self, subscription_id: str) -> bool:
        """إلغاء اشتراك LemonSqueezy."""
        if not self.api_key:
            return False
        try:
            _ls_request("DELETE", f"/subscriptions/{subscription_id}", api_key=self.api_key)
            return True
        except Exception as e:
            logger.error(f"LemonSqueezy cancel_subscription error: {e}")
            return False

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """التحقق من HMAC-SHA256 لـ LemonSqueezy webhooks."""
        if not self.webhook_secret:
            logger.error("LEMONSQUEEZY_WEBHOOK_SECRET is not set")
            return False
        try:
            expected = hmac.new(
                self.webhook_secret.encode("utf-8"),
                payload,
                hashlib.sha256,
            ).hexdigest()
            return hmac.compare_digest(expected, signature)
        except Exception as e:
            logger.error(f"LemonSqueezy webhook verification error: {e}")
            return False
