import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.teams.models import Workspace
from common.models import TimeStampedModel


class ProviderChoices(models.TextChoices):
    STRIPE = "STRIPE", _("Stripe")
    LEMONSQUEEZY = "LEMONSQUEEZY", _("LemonSqueezy")
    PAYMOB = "PAYMOB", _("Paymob")
    PAYPAL = "PAYPAL", _("PayPal")
    PADDLE = "PADDLE", _("Paddle")


class SubscriptionStatusChoices(models.TextChoices):
    ACTIVE = "active", _("Active")
    TRIALLING = "trialling", _("Trialling")
    PAST_DUE = "past_due", _("Past Due")
    CANCELED = "canceled", _("Canceled")
    UNPAID = "unpaid", _("Unpaid")
    INACTIVE = "inactive", _("Inactive")


class PaymentCustomer(TimeStampedModel):
    """ربط مساحة العمل بمعرّف العميل الخارجي لدى بوابة الدفع."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.OneToOneField(
        Workspace,
        on_delete=models.CASCADE,
        related_name="payment_customer",
        verbose_name=_("workspace"),
    )
    provider = models.CharField(
        max_length=20,
        choices=ProviderChoices.choices,
        default=ProviderChoices.STRIPE,
        verbose_name=_("provider"),
    )
    customer_id = models.CharField(
        max_length=255, unique=True, null=True, blank=True, verbose_name=_("customer ID")
    )

    class Meta:
        verbose_name = _("payment customer")
        verbose_name_plural = _("payment customers")

    def __str__(self) -> str:
        return f"{self.workspace.name} ({self.provider})"


class Subscription(TimeStampedModel):
    """تتبع حالة خطة الاشتراك الحالية لمساحة العمل."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.OneToOneField(
        Workspace,
        on_delete=models.CASCADE,
        related_name="subscription",
        verbose_name=_("workspace"),
    )
    provider = models.CharField(
        max_length=20,
        choices=ProviderChoices.choices,
        default=ProviderChoices.STRIPE,
        verbose_name=_("provider"),
    )
    subscription_id = models.CharField(
        max_length=255, unique=True, null=True, blank=True, verbose_name=_("subscription ID")
    )
    plan_id = models.CharField(max_length=255, default="free", verbose_name=_("plan ID"))
    status = models.CharField(
        max_length=50,
        choices=SubscriptionStatusChoices.choices,
        default=SubscriptionStatusChoices.INACTIVE,
        verbose_name=_("status"),
    )
    current_period_end = models.DateTimeField(
        null=True, blank=True, verbose_name=_("current period end")
    )
    cancel_at_period_end = models.BooleanField(
        default=False, verbose_name=_("cancel at period end")
    )

    class Meta:
        verbose_name = _("subscription")
        verbose_name_plural = _("subscriptions")

    def __str__(self) -> str:
        return f"{self.workspace.name} - {self.plan_id} ({self.status})"


class PaymentTransaction(models.Model):
    """سجل تاريخي للعمليات والفواتير المدفوعة."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="payment_transactions",
        verbose_name=_("workspace"),
    )
    provider = models.CharField(
        max_length=20, choices=ProviderChoices.choices, verbose_name=_("provider")
    )
    transaction_id = models.CharField(max_length=255, unique=True, verbose_name=_("transaction ID"))
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("amount"))
    currency = models.CharField(max_length=10, default="USD", verbose_name=_("currency"))
    status = models.CharField(max_length=50, verbose_name=_("status"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("created at"))

    class Meta:
        verbose_name = _("payment transaction")
        verbose_name_plural = _("payment transactions")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.workspace.name}: {self.amount} {self.currency} ({self.status})"
