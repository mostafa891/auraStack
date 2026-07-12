from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.payments.models import PaymentTransaction, Subscription, SubscriptionStatusChoices
from apps.payments.tasks import process_stripe_webhook
from apps.teams.models import Workspace, WorkspaceMember

User = get_user_model()


@pytest.fixture
def test_users_and_workspaces(db):
    user_a = User.objects.create_user(email="user_a@example.com", password="Password123!")
    user_b = User.objects.create_user(email="user_b@example.com", password="Password123!")

    workspace_a = Workspace.objects.create(name="Workspace A", created_by=user_a)
    WorkspaceMember.objects.create(
        workspace=workspace_a, user=user_a, role=WorkspaceMember.RoleChoices.OWNER
    )

    workspace_b = Workspace.objects.create(name="Workspace B", created_by=user_b)
    WorkspaceMember.objects.create(
        workspace=workspace_b, user=user_b, role=WorkspaceMember.RoleChoices.OWNER
    )

    return {
        "user_a": user_a,
        "user_b": user_b,
        "workspace_a": workspace_a,
        "workspace_b": workspace_b,
    }


@pytest.mark.django_db
def test_pricing_view_requires_login(client):
    """التحقق من أن صفحة الأسعار محمية وتطلب تسجيل الدخول."""
    response = client.get(reverse("billing:pricing"))
    assert response.status_code == 302
    assert "login" in response.url


@pytest.mark.django_db
def test_checkout_api_requires_login(client):
    """التحقق من أن API إنشاء الدفع يرفض المستخدمين غير المصرح لهم."""
    # Django-ninja يعيد 401/403 تلقائياً عند غياب الـ auth
    response = client.post(
        "/api/v1/private/billing/checkout",
        data={
            "workspace_id": "893ee8a4-0c2d-48d6-953e-c6e7a2b9f3cd",
            "plan_id": "pro",
            "gateway": "stripe",
        },
        content_type="application/json",
    )
    assert response.status_code in [401, 403]


@pytest.mark.django_db
def test_checkout_api_bola_protection(client, test_users_and_workspaces):
    """التحقق من حماية BOLA/IDOR ومنع مستخدم من ترقية مساحة عمل غير تابعة له."""
    # تسجيل الدخول بالمستخدم A
    client.force_login(test_users_and_workspaces["user_a"])

    # محاولة إنشاء جلسة دفع لمساحة العمل B التابعة للمستخدم B
    response = client.post(
        "/api/v1/private/billing/checkout",
        data={
            "workspace_id": str(test_users_and_workspaces["workspace_b"].id),
            "plan_id": "pro",
            "gateway": "stripe",
        },
        content_type="application/json",
    )

    # يجب أن يرفض الخادم بـ 403 Forbidden
    assert response.status_code == 403


@pytest.mark.django_db
@patch("apps.payments.services.stripe.StripeService.create_customer")
@patch("apps.payments.services.stripe.StripeService.create_checkout_session")
def test_checkout_api_success(
    mock_create_session, mock_create_customer, client, test_users_and_workspaces
):
    """التحقق من نجاح إنشاء جلسة الدفع وطلب التوجيه للمستخدم المصرح له."""
    client.force_login(test_users_and_workspaces["user_a"])

    # محاكاة ردود Stripe
    mock_create_customer.return_value = "cus_mock_123"
    mock_create_session.return_value = "https://checkout.stripe.com/pay_mock_123"

    response = client.post(
        "/api/v1/private/billing/checkout",
        data={
            "workspace_id": str(test_users_and_workspaces["workspace_a"].id),
            "plan_id": "pro_monthly_id",
            "gateway": "stripe",
        },
        content_type="application/json",
    )

    assert response.status_code == 200
    data = response.json()
    assert data["checkout_url"] == "https://checkout.stripe.com/pay_mock_123"


@pytest.mark.django_db
def test_stripe_webhook_missing_signature(client):
    """التحقق من رفض الـ Webhook عند فقدان التوقيع الرقمي."""
    response = client.post(
        "/api/v1/public/billing/webhooks/stripe", data=b"{}", content_type="application/json"
    )
    assert response.status_code == 400


@pytest.mark.django_db
@patch("apps.payments.services.stripe.StripeService.verify_webhook_signature")
def test_process_stripe_webhook_invalid_signature(mock_verify):
    """التحقق من إطلاق خطأ في الخلفية عند فشل التحقق من توقيع الـ Webhook."""
    mock_verify.return_value = False

    with pytest.raises(ValueError, match="Invalid Stripe signature"):
        process_stripe_webhook(b"fake_payload", "invalid_signature")


@pytest.mark.django_db
@patch("apps.payments.services.stripe.StripeService.verify_webhook_signature")
@patch("apps.payments.services.stripe.StripeService.parse_event")
def test_process_stripe_webhook_success(mock_parse, mock_verify, test_users_and_workspaces):
    """التحقق من نجاح معالجة Webhook دفع Stripe وتحديث الاشتراكات والعمليات المالية."""
    mock_verify.return_value = True

    workspace = test_users_and_workspaces["workspace_a"]

    # محاكاة حدث Stripe الناجح
    mock_parse.return_value = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_999",
                "subscription": "sub_stripe_999",
                "amount_total": 1900,
                "currency": "usd",
                "metadata": {"workspace_id": str(workspace.id)},
            }
        },
    }

    # استدعاء دالة الخلفية (المهمة غير المتزامنة التي ينفذها Q2)
    process_stripe_webhook(b"payload", "valid_signature")

    # التحقق من تحديث الاشتراك في قاعدة البيانات
    sub = Subscription.objects.get(workspace=workspace)
    assert sub.status == SubscriptionStatusChoices.ACTIVE
    assert sub.plan_id == "pro"
    assert sub.subscription_id == "sub_stripe_999"

    # التحقق من تسجيل الحركة المالية بنجاح
    tx = PaymentTransaction.objects.get(workspace=workspace)
    assert tx.transaction_id == "cs_test_999"
    assert tx.amount == 19.00
    assert tx.currency == "USD"
    assert tx.status == "succeeded"
