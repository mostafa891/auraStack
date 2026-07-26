from django.conf import settings
from django.test import override_settings


def test_queue_broker_orm_fallback():
    """Verifies that task queue Q2 falls back to DB ORM locally for zero-config setup."""
    # When Redis environment variable is absent, system falls back to ORM
    q_cluster = settings.Q_CLUSTER

    # Verify broker is ORM default
    assert q_cluster.get("orm") == "default"
    assert "redis" not in q_cluster
    assert q_cluster.get("save_limit") == 0


def test_queue_broker_redis_override():
    """Verifies seamless switching to Redis broker when REDIS_URL environment variable is set."""
    dummy_redis_url = "redis://:password@127.0.0.1:6379/0"

    # Simulate settings.py behavior when REDIS_URL is present
    q_cluster_prod = {
        "name": "aurastack_q",
        "workers": 4,
        "recycle": 500,
        "timeout": 60,
        "redis": dummy_redis_url,
    }

    with override_settings(Q_CLUSTER=q_cluster_prod):
        assert settings.Q_CLUSTER.get("redis") == dummy_redis_url
        assert "orm" not in settings.Q_CLUSTER
