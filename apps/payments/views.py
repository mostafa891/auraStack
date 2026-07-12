from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from inertia import render


class PricingView(LoginRequiredMixin, View):
    """عرض خطط الأسعار والاشتراكات المتاحة."""

    def get(self, request):
        stripe_key = getattr(settings, "STRIPE_PUBLISHABLE_KEY", "")
        return render(
            request,
            "Billing/Pricing",
            {
                "stripe_publishable_key": stripe_key,
                "prices": {
                    "pro_monthly": getattr(
                        settings, "STRIPE_PRICE_PRO_MONTHLY", "price_12345_stub"
                    ),
                },
            },
        )


class SubscriptionSettingsView(LoginRequiredMixin, View):
    """عرض صفحة تفاصيل اشتراك مساحة العمل النشطة الحالية."""

    def get(self, request):
        return render(request, "Billing/SubscriptionSettings")
