from apps.payments.models import Subscription, SubscriptionStatusChoices
from apps.payments.plans import PLANS


def get_workspace_plan(workspace) -> str:
    """Retrieves active subscription plan ID for a workspace.

    Returns 'free' if no active subscription exists.
    """
    try:
        sub = workspace.subscription
        if sub and sub.status == SubscriptionStatusChoices.ACTIVE:
            return sub.plan_id
    except Subscription.DoesNotExist:
        pass
    return "free"


def get_plan_limit(workspace, limit_key: str):
    """Retrieves specific quota limit from active workspace subscription plan.

    Example: get_plan_limit(workspace, 'max_members') -> 3 or 20
    """
    plan_id = get_workspace_plan(workspace)
    plan = PLANS.get(plan_id, PLANS["free"])
    return plan.get(limit_key)


def get_active_plans_data():
    """Retrieves active subscription plans with features from database for page views."""
    try:
        from apps.payments.models import Plan

        plans = (
            Plan.objects.filter(is_active=True)
            .prefetch_related("features")
            .order_by("sorting_order", "price_monthly")
        )
        if not plans.exists():
            raise ValueError("No plans in DB")
    except Exception:
        # Fallback default plans list if DB table is not created/populated yet
        return [
            {
                "id": "free",
                "name": "Free Plan",
                "description": "Perfect for individuals and exploring the engine",
                "price_monthly": "0.00",
                "price_yearly": "0.00",
                "max_members": 3,
                "is_popular": False,
                "features": [
                    {"feature_text": "Up to 3 workspace members", "is_highlighted": False},
                    {"feature_text": "Email & Community Support", "is_highlighted": False},
                    {"feature_text": "Core RBAC & MFA Security", "is_highlighted": False},
                ],
            },
            {
                "id": "pro",
                "name": "Pro Plan",
                "description": "Built for growing teams & fast-scaling startups",
                "price_monthly": "29.00",
                "price_yearly": "290.00",
                "max_members": 20,
                "is_popular": True,
                "features": [
                    {"feature_text": "Up to 20 workspace members", "is_highlighted": True},
                    {
                        "feature_text": "Stripe, Paymob, PayPal & Paddle Gateways",
                        "is_highlighted": True,
                    },
                    {
                        "feature_text": "Priority Support & Automated Backups",
                        "is_highlighted": False,
                    },
                    {"feature_text": "Advanced Workspace Analytics", "is_highlighted": False},
                ],
            },
            {
                "id": "enterprise",
                "name": "Enterprise Plan",
                "description": "For scale-ups requiring dedicated support & SLAs",
                "price_monthly": "99.00",
                "price_yearly": "990.00",
                "max_members": 100,
                "is_popular": False,
                "features": [
                    {"feature_text": "Unlimited Workspace Members", "is_highlighted": True},
                    {"feature_text": "Dedicated Infra & 99.9% Uptime SLA", "is_highlighted": True},
                    {"feature_text": "24/7 Dedicated Account Manager", "is_highlighted": True},
                ],
            },
        ]

    result = []
    for plan in plans:
        result.append(
            {
                "id": plan.id,
                "name": plan.name,
                "description": plan.description,
                "price_monthly": str(plan.price_monthly),
                "price_yearly": str(plan.price_yearly),
                "max_members": plan.max_members,
                "is_popular": plan.is_popular,
                "features": [
                    {"feature_text": f.feature_text, "is_highlighted": f.is_highlighted}
                    for f in plan.features.all()
                ],
            }
        )
    return result
