import datetime

from django.db import connection
from django.http import JsonResponse
from django.utils.timezone import now
from django_q.models import Task


def health_check(request):
    """
    نقطة فحص صحة النظام للتحقق من الاتصال بالخدمات الحيوية:
    1. قاعدة البيانات (Database Connectivity)
    2. حالة خادم المهام Q2 (Recent Task Executions)
    """
    health_status = {
        "status": "healthy",
        "timestamp": now().isoformat(),
        "services": {"database": "unknown", "q2_worker": "unknown"},
    }

    # 1. فحص قاعدة البيانات
    try:
        connection.ensure_connection()
        health_status["services"]["database"] = "up"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["services"]["database"] = f"down: {str(e)}"

    # 2. فحص حالة خادم Q2 (البحث عن مهام تمت معالجتها مؤخراً)
    try:
        recent_tasks_exist = Task.objects.filter(
            started__gte=now() - datetime.timedelta(hours=24)
        ).exists()
        health_status["services"]["q2_worker"] = (
            "active" if recent_tasks_exist else "idle_no_recent_tasks"
        )
    except Exception as e:
        health_status["services"]["q2_worker"] = f"error: {str(e)}"

    status_code = 200 if health_status["status"] == "healthy" else 503
    return JsonResponse(health_status, status=status_code)
