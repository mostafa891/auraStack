from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model

from apps.teams.models import Workspace

User = get_user_model()


@pytest.fixture
def workspace_with_owner(db):
    user = User.objects.create_user(email="owner@example.com", password="Password123!")
    workspace = Workspace.objects.create(name="Stripe Test Org", created_by=user)
    return workspace


@pytest.mark.django_db
def test_stripe_webhook_unauthorized_missing_signature(client):
    """التحقق من رفض الخادم لمعاملة Stripe Webhook في حال غياب التوقيع الرقمي (400 Bad Request)."""
    response = client.post(
        "/api/v1/public/billing/webhooks/stripe", data="{}", content_type="application/json"
    )
    assert response.status_code == 400


@pytest.mark.django_db
@patch("apps.payments.services.stripe.StripeService.verify_webhook_signature")
def test_stripe_webhook_invalid_signature(mock_verify, client):
    """التحقق من إيقاف المعالجة وعدم ترقية الحساب عند إرسال توقيع تالف أو مزيف."""
    mock_verify.return_value = False

    response = client.post(
        "/api/v1/public/billing/webhooks/stripe",
        data='{"type":"checkout.session.completed"}',
        content_type="application/json",
        HTTP_STRIPE_SIGNATURE="t=123,v1=badsignature",
    )

    # الـ API تعيد 200 فوراً لتفادي هجمات DoS وتفوض المهمة لـ Q2.
    # لكن مهمة Q2 ستفشل داخلياً وتطلق خطأ عند التحقق.
    assert response.status_code == 200

    from apps.payments.tasks import process_stripe_webhook

    with pytest.raises(ValueError, match="Invalid Stripe signature"):
        process_stripe_webhook(b"payload", "badsignature")
