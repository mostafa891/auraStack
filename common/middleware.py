from django.http import HttpRequest
from inertia import share


class ShareUserDataMiddleware:
    """كود وسيط لمشاركة تفاصيل المستخدم الحالي مع واجهات Inertia بشكل آمن."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        # في بيئة Inertia، نقوم بنشر الحساب والمعلومات المشتركة في كل استجابة
        if request.user and request.user.is_authenticated:
            # جلب مساحات العمل التي ينتمي إليها المستخدم مع أدواره فيها بشكل فعال
            memberships = list(request.user.workspace_memberships.select_related("workspace"))
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

            # جلب مساحة العمل النشطة من الجلسة
            active_workspace_id = request.session.get("active_workspace_id")
            active_workspace = None

            if active_workspace_id:
                active_mem = next(
                    (m for m in memberships if str(m.workspace.id) == active_workspace_id), None
                )
                if active_mem:
                    active_workspace = {
                        "id": str(active_mem.workspace.id),
                        "name": active_mem.workspace.name,
                        "slug": active_mem.workspace.slug,
                        "role": active_mem.role,
                        "role_display": active_mem.get_role_display(),
                    }
                else:
                    request.session.pop("active_workspace_id", None)

            # إذا لم تكن هناك مساحة نشطة، نختار مساحة العمل الأولى تلقائياً
            if not active_workspace and workspaces_data:
                first_mem = memberships[0]
                request.session["active_workspace_id"] = str(first_mem.workspace.id)
                active_workspace = {
                    "id": str(first_mem.workspace.id),
                    "name": first_mem.workspace.name,
                    "slug": first_mem.workspace.slug,
                    "role": first_mem.role,
                    "role_display": first_mem.get_role_display(),
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

        response = self.get_response(request)
        return response
