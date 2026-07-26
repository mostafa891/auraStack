from django.contrib.auth import get_user_model

from apps.payments.models import Subscription, SubscriptionStatusChoices
from apps.teams.models import Workspace


def admin_dashboard_callback(request, context):
    """
    Computes key performance metrics for the admin dashboard:
    1. Total registered users
    2. Total workspaces count
    3. Active paid subscriptions count
    4. Estimated Monthly Recurring Revenue (MRR)
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
