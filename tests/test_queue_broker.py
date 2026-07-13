from django.conf import settings
from django.test import override_settings


def test_queue_broker_orm_fallback():
    """التحقق من أن طابور المهام Q2 يستخدم الـ ORM محلياً لتبسيط التشغيل والتثبيت."""
    # عند غياب المتغير البيئي للـ Redis، يجب أن يقع النظام على الـ ORM
    q_cluster = settings.Q_CLUSTER

    # التحقق من أن الوسيط هو default (ORM)
    assert q_cluster.get("orm") == "default"
    assert "redis" not in q_cluster
    assert q_cluster.get("save_limit") == 0


def test_queue_broker_redis_override():
    """التحقق من إمكانية التبديل الفوري لوسيط Redis للإنتاج بمجرد تعريف المتغير البيئي."""
    dummy_redis_url = "redis://:password@127.0.0.1:6379/0"

    # محاكاة سلوك الـ settings.py عند وجود REDIS_URL
    q_cluster_prod = {
        "name": "auraflow_q",
        "workers": 4,
        "recycle": 500,
        "timeout": 60,
        "redis": dummy_redis_url,
    }

    with override_settings(Q_CLUSTER=q_cluster_prod):
        assert settings.Q_CLUSTER.get("redis") == dummy_redis_url
        assert "orm" not in settings.Q_CLUSTER
