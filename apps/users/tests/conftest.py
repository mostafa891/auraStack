import os

import pytest
from django.test import Client

from apps.users.models import CustomUser

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"


@pytest.fixture
def client():
    """Provides default Django test client instance."""
    return Client()


@pytest.fixture
def test_user(db):
    """Provides a default test user instance in the database."""
    user = CustomUser.objects.create_user(
        email="test@aurastack.com",
        password="TestPassword123!",
        first_name="Test",
        last_name="User",
        language="en",
        theme="SYSTEM",
        timezone="UTC",
    )
    return user
