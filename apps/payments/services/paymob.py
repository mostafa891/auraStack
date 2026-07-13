import hashlib
import hmac
import json
import logging
import urllib.parse
import urllib.request

from django.conf import settings

from apps.payments.interfaces import BasePaymentGateway

logger = logging.getLogger(__name__)

PAYMOB_BASE_URL = "https://accept.paymob.com/api"


def _paymob_post(endpoint: str, payload: dict) -> dict:
    """دالة مساعدة لإرسال طلبات POST لـ Paymob API."""
    url = f"{PAYMOB_BASE_URL}{endpoint}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


class PaymobService(BasePaymentGateway):
    """
    تطبيق كامل لبوابة الدفع Paymob (السوق المصري والعربي).

    المتغيرات المطلوبة في .env:
        PAYMOB_API_KEY       — مفتاح API من لوحة تحكم Paymob
        PAYMOB_INTEGRATION_ID — معرّف الـ integration (بطاقة ائتمان أو محافظ)
        PAYMOB_IFRAME_ID     — معرّف الـ iframe لصفحة الدفع
        PAYMOB_HMAC_SECRET   — مفتاح HMAC للتحقق من صحة الـ webhooks
    """

    def __init__(self):
        self.api_key = getattr(settings, "PAYMOB_API_KEY", "")
        self.integration_id = getattr(settings, "PAYMOB_INTEGRATION_ID", "")
        self.iframe_id = getattr(settings, "PAYMOB_IFRAME_ID", "")
        self.hmac_secret = getattr(settings, "PAYMOB_HMAC_SECRET", "")

    def _authenticate(self) -> str:
        """الخطوة 1: المصادقة والحصول على auth_token."""
        if not self.api_key:
            raise ValueError("PAYMOB_API_KEY is not configured")
        response = _paymob_post("/auth/tokens", {"api_key": self.api_key})
        return response["token"]

    def _register_order(self, auth_token: str, amount_cents: int, workspace_id: str) -> str:
        """الخطوة 2: تسجيل الطلب والحصول على order_id."""
        payload = {
            "auth_token": auth_token,
            "delivery_needed": False,
            "amount_cents": amount_cents,
            "currency": "EGP",
            "merchant_order_id": workspace_id[:40],  # max 40 chars
            "items": [],
        }
        response = _paymob_post("/ecommerce/orders", payload)
        return str(response["id"])

    def _get_payment_key(
        self, auth_token: str, order_id: str, amount_cents: int, billing_data: dict
    ) -> str:
        """الخطوة 3: الحصول على payment_key لفتح iframe الدفع."""
        payload = {
            "auth_token": auth_token,
            "amount_cents": amount_cents,
            "expiration": 3600,
            "order_id": order_id,
            "billing_data": billing_data,
            "currency": "EGP",
            "integration_id": int(self.integration_id),
            "lock_order_when_paid": True,
        }
        response = _paymob_post("/acceptance/payment_keys", payload)
        return response["token"]

    def create_customer(self, workspace_id: str, email: str) -> str:
        """Paymob لا يحتاج عملاء مسبقاً — نُرجع workspace_id كمعرّف."""
        return workspace_id

    def create_checkout_session(
        self,
        customer_id: str,
        plan_id: str,
        success_url: str,
        cancel_url: str,
        metadata: dict = None,
    ) -> str:
        """
        إنشاء رابط الدفع عبر Paymob iframe.
        يُرجع رابط iframe الكامل.
        """
        if not self.api_key or not self.integration_id or not self.iframe_id:
            raise ValueError(
                "Paymob is not fully configured. "
                "Set PAYMOB_API_KEY, PAYMOB_INTEGRATION_ID, PAYMOB_IFRAME_ID in .env"
            )

        # سعر ثابت للتجربة — في الإنتاج يُحسب من الخطة
        amount_cents = 19900  # 199 جنيه مصري = 19900 قرش

        billing_data = {
            "apartment": "NA",
            "email": metadata.get("email", "customer@example.com")
            if metadata
            else "customer@example.com",
            "floor": "NA",
            "first_name": "AuraFlow",
            "street": "NA",
            "building": "NA",
            "phone_number": "+20100000000",
            "shipping_method": "NA",
            "postal_code": "NA",
            "city": "Cairo",
            "country": "EG",
            "last_name": "Customer",
            "state": "Cairo",
        }

        auth_token = self._authenticate()
        workspace_id = customer_id
        order_id = self._register_order(auth_token, amount_cents, workspace_id)
        payment_key = self._get_payment_key(auth_token, order_id, amount_cents, billing_data)

        return f"https://accept.paymob.com/api/acceptance/iframes/{self.iframe_id}?payment_token={payment_key}"

    def cancel_subscription(self, subscription_id: str) -> bool:
        """Paymob لا يدعم إلغاء الاشتراكات عبر API مباشرة — يتم يدوياً من لوحة التحكم."""
        logger.warning(
            "Paymob subscription cancellation must be done manually from Paymob dashboard. "
            f"Subscription ID: {subscription_id}"
        )
        return True

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """التحقق من HMAC-SHA512 لـ Paymob webhooks."""
        if not self.hmac_secret:
            logger.error("PAYMOB_HMAC_SECRET is not set — webhook signature verification skipped")
            return False
        try:
            body = json.loads(payload.decode("utf-8"))
            obj = body.get("obj", {})
            # بناء سلسلة HMAC بترتيب Paymob المحدد
            concatenated = "".join(
                str(obj.get(k, ""))
                for k in [
                    "amount_cents",
                    "created_at",
                    "currency",
                    "error_occured",
                    "has_parent_transaction",
                    "id",
                    "integration_id",
                    "is_3d_secure",
                    "is_auth",
                    "is_capture",
                    "is_refunded",
                    "is_standalone_payment",
                    "is_voided",
                    "order",
                    "owner",
                    "pending",
                    "source_data.pan",
                    "source_data.sub_type",
                    "source_data.type",
                    "success",
                ]
            )
            expected = hmac.new(
                self.hmac_secret.encode("utf-8"),
                concatenated.encode("utf-8"),
                hashlib.sha512,
            ).hexdigest()
            return hmac.compare_digest(expected, signature)
        except Exception as e:
            logger.error(f"Paymob webhook verification error: {e}")
            return False
