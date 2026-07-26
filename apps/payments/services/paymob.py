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
    """Helper utility for sending POST requests to Paymob API."""
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
    """Paymob payment gateway integration (MENA region).

    Required environment variables:
        PAYMOB_API_KEY        - API secret key
        PAYMOB_INTEGRATION_ID - Integration ID (card or wallet)
        PAYMOB_IFRAME_ID      - Payment iframe template ID
        PAYMOB_HMAC_SECRET    - Webhook HMAC secret
    """

    def __init__(self):
        self.api_key = getattr(settings, "PAYMOB_API_KEY", "")
        self.integration_id = getattr(settings, "PAYMOB_INTEGRATION_ID", "")
        self.iframe_id = getattr(settings, "PAYMOB_IFRAME_ID", "")
        self.hmac_secret = getattr(settings, "PAYMOB_HMAC_SECRET", "")

    def _authenticate(self) -> str:
        """Step 1: Authenticate and obtain auth_token."""
        if not self.api_key:
            raise ValueError("PAYMOB_API_KEY is not configured")
        response = _paymob_post("/auth/tokens", {"api_key": self.api_key})
        return response["token"]

    def _register_order(self, auth_token: str, amount_cents: int, workspace_id: str) -> str:
        """Step 2: Register merchant order and obtain order_id."""
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
        """Step 3: Generate payment_key to render payment iframe."""
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
        """Paymob does not require pre-created customers; returns workspace_id as reference."""
        return workspace_id

    def create_checkout_session(
        self,
        customer_id: str,
        plan_id: str,
        success_url: str,
        cancel_url: str,
        metadata: dict = None,
    ) -> str:
        """Generates Paymob payment iframe checkout URL."""
        if not self.api_key or not self.integration_id or not self.iframe_id:
            raise ValueError(
                "Paymob is not fully configured. "
                "Set PAYMOB_API_KEY, PAYMOB_INTEGRATION_ID, PAYMOB_IFRAME_ID in .env"
            )

        # Base amount in cents (199 EGP = 19900 cents)
        amount_cents = 19900

        billing_data = {
            "apartment": "NA",
            "email": metadata.get("email", "customer@example.com")
            if metadata
            else "customer@example.com",
            "floor": "NA",
            "first_name": "auraStack",
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
        """Paymob subscriptions are managed manually from Paymob Dashboard."""
        logger.warning(
            "Paymob subscription cancellation must be done manually from Paymob dashboard. "
            f"Subscription ID: {subscription_id}"
        )
        return True

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verifies HMAC-SHA512 signature for Paymob webhooks."""
        if not self.hmac_secret:
            logger.error("PAYMOB_HMAC_SECRET is not set — webhook signature verification skipped")
            return False
        try:
            body = json.loads(payload.decode("utf-8"))
            obj = body.get("obj", {})
            # Construct HMAC concatenated string in Paymob sequence
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
