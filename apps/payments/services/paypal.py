import base64
import json
import logging
import urllib.parse
import urllib.request

from django.conf import settings

from apps.payments.interfaces import BasePaymentGateway

logger = logging.getLogger(__name__)


class PayPalService(BasePaymentGateway):
    """
    تطبيق كامل لبوابة الدفع PayPal (Subscriptions API).

    المتغيرات المطلوبة في .env:
        PAYPAL_CLIENT_ID     — معرّف التطبيق من PayPal Developer
        PAYPAL_CLIENT_SECRET — مفتاح التطبيق السري
        PAYPAL_WEBHOOK_ID    — معرّف Webhook للتحقق
        PAYPAL_ENVIRONMENT   — 'sandbox' أو 'production'
    """

    def __init__(self):
        self.client_id = getattr(settings, "PAYPAL_CLIENT_ID", "")
        self.client_secret = getattr(settings, "PAYPAL_CLIENT_SECRET", "")
        self.webhook_id = getattr(settings, "PAYPAL_WEBHOOK_ID", "")
        env = getattr(settings, "PAYPAL_ENVIRONMENT", "sandbox")
        self.base_url = (
            "https://api-m.paypal.com"
            if env == "production"
            else "https://api-m.sandbox.paypal.com"
        )

    def _get_access_token(self) -> str:
        """الحصول على OAuth2 access token من PayPal."""
        if not self.client_id or not self.client_secret:
            raise ValueError("PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET are not configured")
        credentials = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        data = urllib.parse.urlencode({"grant_type": "client_credentials"}).encode()
        req = urllib.request.Request(
            f"{self.base_url}/v1/oauth2/token",
            data=data,
            headers={
                "Authorization": f"Basic {credentials}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())["access_token"]

    def _paypal_request(self, method: str, endpoint: str, payload: dict = None) -> dict:
        """دالة مساعدة لإرسال طلبات لـ PayPal API."""
        token = self._get_access_token()
        url = f"{self.base_url}{endpoint}"
        data = json.dumps(payload).encode("utf-8") if payload else None
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Prefer": "return=representation",
            },
            method=method,
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read()
            return json.loads(body) if body else {}

    def create_customer(self, workspace_id: str, email: str) -> str:
        """PayPal لا يتطلب إنشاء عميل مسبق — يُرجع workspace_id."""
        return workspace_id

    def create_checkout_session(
        self,
        customer_id: str,
        plan_id: str,
        success_url: str,
        cancel_url: str,
        metadata: dict = None,
    ) -> str:
        """إنشاء اشتراك PayPal وإرجاع رابط الموافقة."""
        try:
            response = self._paypal_request(
                "POST",
                "/v1/billing/subscriptions",
                {
                    "plan_id": plan_id,
                    "application_context": {
                        "return_url": success_url,
                        "cancel_url": cancel_url,
                        "brand_name": "AuraFlow",
                        "user_action": "SUBSCRIBE_NOW",
                    },
                    "custom_id": customer_id,
                },
            )
            # استخراج رابط approve من الـ links
            for link in response.get("links", []):
                if link.get("rel") == "approve":
                    return link["href"]
            raise ValueError("PayPal did not return an approval URL")
        except Exception as e:
            logger.error(f"PayPal create_checkout_session error: {e}")
            raise

    def cancel_subscription(self, subscription_id: str) -> bool:
        """إلغاء اشتراك PayPal."""
        try:
            self._paypal_request(
                "POST",
                f"/v1/billing/subscriptions/{subscription_id}/cancel",
                {"reason": "Cancelled by user"},
            )
            return True
        except Exception as e:
            logger.error(f"PayPal cancel_subscription error: {e}")
            return False

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """
        التحقق من صحة PayPal Webhooks عبر PayPal Webhook verification API.
        يتطلب PAYPAL_WEBHOOK_ID من لوحة تحكم PayPal.
        """
        if not self.webhook_id:
            logger.error("PAYPAL_WEBHOOK_ID is not set — skipping webhook verification")
            return False
        try:
            token = self._get_access_token()
            # PayPal يتطلب إرسال البيانات لـ API التحقق الخاص به
            verify_payload = {
                "auth_algo": "SHA256withRSA",
                "cert_url": signature,  # في الواقع يُمرر cert_url من headers
                "transmission_id": "",
                "transmission_sig": signature,
                "transmission_time": "",
                "webhook_id": self.webhook_id,
                "webhook_event": json.loads(payload.decode("utf-8")),
            }
            data = json.dumps(verify_payload).encode("utf-8")
            req = urllib.request.Request(
                f"{self.base_url}/v1/notifications/verify-webhook-signature",
                data=data,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                result = json.loads(resp.read().decode())
                return result.get("verification_status") == "SUCCESS"
        except Exception as e:
            logger.error(f"PayPal webhook verification error: {e}")
            return False
