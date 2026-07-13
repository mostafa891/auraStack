from django.contrib.auth import get_user_model

from apps.payments.models import Subscription, SubscriptionStatusChoices
from apps.teams.models import Workspace


def admin_dashboard_callback(request, context):
    """
    يقوم بحساب وعرض مؤشرات الأداء الحيوية في لوحة تحكم الأدمن:
    1. عدد المستخدمين الكلي
    2. عدد مساحات العمل الكلية
    3. عدد الاشتراكات المدفوعة النشطة
    4. تقدير الإيرادات المتكررة شهرياً (MRR)
    """
    User = get_user_model()

    total_users = User.objects.count()
    total_workspaces = Workspace.objects.count()

    active_subs = Subscription.objects.filter(
        status=SubscriptionStatusChoices.ACTIVE, plan_id="pro"
    ).count()

    # MRR (Pro plan is $19/month by default)
    mrr = active_subs * 19.0

    context.update(
        {
            "total_users": total_users,
            "total_workspaces": total_workspaces,
            "active_subs": active_subs,
            "mrr": mrr,
        }
    )

    return context
