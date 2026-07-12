from django.urls import path

from apps.payments.views import PricingView, SubscriptionSettingsView

app_name = "billing"

urlpatterns = [
    path("pricing/", PricingView.as_view(), name="pricing"),
    path("subscription/", SubscriptionSettingsView.as_view(), name="subscription"),
]
