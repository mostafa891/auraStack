from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from apps.payments.models import (
    PaymentCustomer,
    PaymentTransaction,
    Plan,
    PlanFeature,
    Subscription,
)


class PlanFeatureInline(TabularInline):
    model = PlanFeature
    extra = 1


@admin.register(Plan)
class PlanAdmin(ModelAdmin):
    list_display = [
        "name",
        "id",
        "price_monthly",
        "price_yearly",
        "max_members",
        "is_popular",
        "is_active",
    ]
    list_editable = ["is_active", "is_popular", "price_monthly"]
    search_fields = ["name", "id"]
    inlines = [PlanFeatureInline]


@admin.register(Subscription)
class SubscriptionAdmin(ModelAdmin):
    list_display = ["workspace", "plan_id", "status", "provider", "current_period_end"]
    list_filter = ["status", "provider"]
    search_fields = ["workspace__name", "subscription_id"]


@admin.register(PaymentCustomer)
class PaymentCustomerAdmin(ModelAdmin):
    list_display = ["workspace", "provider", "customer_id"]
    search_fields = ["workspace__name", "customer_id"]


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(ModelAdmin):
    list_display = ["workspace", "amount", "currency", "provider", "status", "created_at"]
    list_filter = ["provider", "status"]
    search_fields = ["workspace__name", "transaction_id"]
