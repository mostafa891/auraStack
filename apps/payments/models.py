import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.teams.models import Workspace
from common.models import SoftDeleteModel, TimeStampedModel


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


class Plan(TimeStampedModel):
    """Dynamically defined subscription plans."""

    id = models.CharField(
        max_length=100, primary_key=True, help_text=_("Unique plan ID (e.g. free, pro, enterprise)")
    )
    name = models.CharField(max_length=255, verbose_name=_("plan name"))
    description = models.TextField(blank=True, default="", verbose_name=_("description"))
    price_monthly = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, verbose_name=_("monthly price")
    )
    price_yearly = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00, verbose_name=_("yearly price")
    )
    stripe_price_id = models.CharField(
        max_length=255, blank=True, default="", verbose_name=_("Stripe price ID")
    )
    paymob_plan_id = models.CharField(
        max_length=255, blank=True, default="", verbose_name=_("Paymob plan ID")
    )
    max_members = models.IntegerField(default=3, verbose_name=_("maximum workspace members"))
    is_active = models.BooleanField(default=True, verbose_name=_("is active"))
    is_popular = models.BooleanField(default=False, verbose_name=_("highlight as popular"))
    sorting_order = models.IntegerField(default=0, verbose_name=_("sorting order"))

    class Meta:
        verbose_name = _("plan")
        verbose_name_plural = _("plans")
        ordering = ["sorting_order", "price_monthly"]

    def __str__(self) -> str:
        return f"{self.name} (${self.price_monthly}/mo)"


class PlanFeature(models.Model):
    """Specific features belonging to a subscription plan."""

    plan = models.ForeignKey(
        Plan, on_delete=models.CASCADE, related_name="features", verbose_name=_("plan")
    )
    feature_text = models.CharField(max_length=255, verbose_name=_("feature text"))
    is_highlighted = models.BooleanField(default=False, verbose_name=_("is highlighted"))

    class Meta:
        verbose_name = _("plan feature")
        verbose_name_plural = _("plan features")

    def __str__(self) -> str:
        return f"{self.plan.name}: {self.feature_text}"


class PaymentCustomer(SoftDeleteModel, TimeStampedModel):
    """Maps workspace instance to external payment gateway customer ID."""

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


class Subscription(SoftDeleteModel, TimeStampedModel):
    """Tracks workspace subscription plan status and validity period."""

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
    """Historical audit ledger for transactions and invoices."""

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
