from abc import ABC, abstractmethod
from typing import Any


class BasePaymentGateway(ABC):
    @abstractmethod
    def create_customer(self, workspace_id: str, email: str) -> str:
        """إنشاء أو جلب العميل من بوابة الدفع."""
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
        """توليد رابط الدفع لجلسة جديدة (Checkout Session)."""
        pass

    @abstractmethod
    def cancel_subscription(self, subscription_id: str) -> bool:
        """إلغاء الاشتراك النشط لدى البوابة."""
        pass

    @abstractmethod
    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """التحقق التواقيع والـ HMAC الخاص بالإشارات الواردة."""
        pass
