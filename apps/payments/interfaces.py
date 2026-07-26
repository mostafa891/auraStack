from abc import ABC, abstractmethod
from typing import Any


class BasePaymentGateway(ABC):
    @abstractmethod
    def create_customer(self, workspace_id: str, email: str) -> str:
        """Creates or retrieves customer reference from payment provider."""
        pass

    @abstractmethod
    def create_checkout_session(
        self,
        customer_id: str,
        plan_id: str,
        success_url: str,
        cancel_url: str,
        metadata: dict[str, Any] = None,
    ) -> str:
        """Generates checkout URL for a new payment session."""
        pass

    @abstractmethod
    def cancel_subscription(self, subscription_id: str) -> bool:
        """Cancels active subscription with payment provider."""
        pass

    @abstractmethod
    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verifies incoming webhook payload digital signature / HMAC digest."""
        pass
