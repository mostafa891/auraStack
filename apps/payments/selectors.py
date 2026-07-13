from apps.payments.models import Subscription, SubscriptionStatusChoices
from apps.payments.plans import PLANS


def get_workspace_plan(workspace) -> str:
    """
    جلب مُعرّف الخطة النشطة لمساحة العمل.
    يُرجع 'free' إذا لم يكن هناك اشتراك نشط.
    """
    try:
        sub = workspace.subscription
        if sub and sub.status == SubscriptionStatusChoices.ACTIVE:
            return sub.plan_id
    except Subscription.DoesNotExist:
        pass
    return "free"


def get_plan_limit(workspace, limit_key: str):
    """
    جلب قيمة حد محدد من خطة مساحة العمل النشطة.
    مثال: get_plan_limit(workspace, 'max_members') → 3 أو 20
    """
    plan_id = get_workspace_plan(workspace)
    plan = PLANS.get(plan_id, PLANS["free"])
    return plan.get(limit_key)
