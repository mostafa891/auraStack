from django.http import HttpRequest
from inertia import share


class ShareUserDataMiddleware:
    """كود وسيط لمشاركة تفاصيل المستخدم الحالي مع واجهات Inertia بشكل آمن."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        request.active_workspace = None
        # في بيئة Inertia، نقوم بنشر الحساب والمعلومات المشتركة في كل استجابة
        if request.user and request.user.is_authenticated:
            user_lang = request.user.language
            if (
                user_lang
                and hasattr(request, "session")
                and request.session.get("_language") != user_lang
            ):
                request.session["_language"] = user_lang
                from django.utils import translation

                translation.activate(user_lang)
                request.LANGUAGE_CODE = translation.get_language()

            from apps.teams.selectors import get_active_workspace, list_user_workspaces

            # جلب مساحات العمل التي ينتمي إليها المستخدم
            # مع أدواره فيها بشكل فعال باستخدام الـ Selector
            memberships = list_user_workspaces(request.user)
            workspaces_data = [
                {
                    "id": str(m.workspace.id),
                    "name": m.workspace.name,
                    "slug": m.workspace.slug,
                    "role": m.role,
                    "role_display": m.get_role_display(),
                }
                for m in memberships
            ]

            # جلب مساحة العمل النشطة من الجلسة باستخدام الـ Selector
            active_workspace_id = request.session.get("active_workspace_id")
            active_workspace = None

            from apps.payments.models import Subscription, SubscriptionStatusChoices
            from apps.payments.plans import PLANS

            if active_workspace_id:
                active_mem = get_active_workspace(request.user, active_workspace_id)
                if active_mem:
                    request.active_workspace = active_mem.workspace
                    # جلب تفاصيل الاشتراك الحالية
                    sub = Subscription.objects.filter(workspace_id=active_workspace_id).first()
                    if sub:
                        plan_id = sub.plan_id
                        sub_status = sub.status
                        current_period_end = (
                            sub.current_period_end.isoformat() if sub.current_period_end else None
                        )
                        cancel_at_period_end = sub.cancel_at_period_end
                    else:
                        plan_id = "free"
                        sub_status = SubscriptionStatusChoices.ACTIVE
                        current_period_end = None
                        cancel_at_period_end = False

                    plan_limits = PLANS.get(plan_id, PLANS["free"])
                    max_members = plan_limits["max_members"]
                    member_count = active_mem.workspace.members.count()

                    is_locked = False
                    if plan_id != "free" and sub_status != SubscriptionStatusChoices.ACTIVE:
                        is_locked = True
                    elif member_count > max_members:
                        is_locked = True

                    active_workspace = {
                        "id": str(active_mem.workspace.id),
                        "name": active_mem.workspace.name,
                        "slug": active_mem.workspace.slug,
                        "role": active_mem.role,
                        "role_display": active_mem.get_role_display(),
                        "subscription": {
                            "plan_id": plan_id,
                            "status": sub_status,
                            "current_period_end": current_period_end,
                            "cancel_at_period_end": cancel_at_period_end,
                            "is_locked": is_locked,
                            "max_members": max_members,
                            "member_count": member_count,
                        },
                    }
                else:
                    request.session.pop("active_workspace_id", None)

            # إذا لم تكن هناك مساحة نشطة، نختار مساحة العمل الأولى تلقائياً
            if not active_workspace and memberships:
                first_mem = memberships[0]
                request.active_workspace = first_mem.workspace
                request.session["active_workspace_id"] = str(first_mem.workspace.id)
                sub = Subscription.objects.filter(workspace_id=str(first_mem.workspace.id)).first()
                if sub:
                    plan_id = sub.plan_id
                    sub_status = sub.status
                    current_period_end = (
                        sub.current_period_end.isoformat() if sub.current_period_end else None
                    )
                    cancel_at_period_end = sub.cancel_at_period_end
                else:
                    plan_id = "free"
                    sub_status = SubscriptionStatusChoices.ACTIVE
                    current_period_end = None
                    cancel_at_period_end = False

                plan_limits = PLANS.get(plan_id, PLANS["free"])
                max_members = plan_limits["max_members"]
                member_count = first_mem.workspace.members.count()

                is_locked = False
                if plan_id != "free" and sub_status != SubscriptionStatusChoices.ACTIVE:
                    is_locked = True
                elif member_count > max_members:
                    is_locked = True

                active_workspace = {
                    "id": str(first_mem.workspace.id),
                    "name": first_mem.workspace.name,
                    "slug": first_mem.workspace.slug,
                    "role": first_mem.role,
                    "role_display": first_mem.get_role_display(),
                    "subscription": {
                        "plan_id": plan_id,
                        "status": sub_status,
                        "current_period_end": current_period_end,
                        "cancel_at_period_end": cancel_at_period_end,
                        "is_locked": is_locked,
                        "max_members": max_members,
                        "member_count": member_count,
                    },
                }

            share(
                request,
                auth={
                    "user": {
                        "id": str(request.user.id),
                        "email": request.user.email,
                        "avatar_url": request.user.avatar_url
                        or f"https://ui-avatars.com/api/?name={request.user.email}&background=6366f1&color=fff",
                        "language": request.user.language,
                        "theme": request.user.theme,
                        "timezone": request.user.timezone,
                        "is_staff": request.user.is_staff,
                        "is_superuser": request.user.is_superuser,
                    },
                    "workspaces": workspaces_data,
                    "active_workspace": active_workspace,
                },
            )
        else:
            share(
                request,
                auth={
                    "user": None,
                    "workspaces": [],
                    "active_workspace": None,
                },
            )

        # مشاركة الرسائل الفورية (Flash Messages) الخاصة بـ Django مع Inertia
        from django.contrib.messages import get_messages

        django_messages = []
        for message in get_messages(request):
            django_messages.append(
                {
                    "message": message.message,
                    "level": message.level,
                    "tags": message.tags or "",
                }
            )
        share(request, flash=django_messages)

        # Get active language code and share with Inertia
        from django.utils import translation

        share(request, locale=translation.get_language()[:2])

        response = self.get_response(request)
        if request.user and request.user.is_authenticated:
            user_lang = request.user.language
            from django.conf import settings

            if user_lang and request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME) != user_lang:
                response.set_cookie(settings.LANGUAGE_COOKIE_NAME, user_lang)
        return response
