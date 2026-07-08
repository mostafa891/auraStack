import os

import pytest
from django.test import Client

from apps.users.models import CustomUser

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"


@pytest.fixture
def client():
    """تجهيز عميل الاختبارات الافتراضي لـ Django."""
    return Client()


@pytest.fixture
def test_user(db):
    """تجهيز مستخدم تجريبي مسجل في قاعدة البيانات."""
    user = CustomUser.objects.create_user(
        email="test@auraflow.com",
        password="TestPassword123!",
        first_name="Test",
        last_name="User",
        language="en",
        theme="SYSTEM",
        timezone="UTC",
    )
    return user
