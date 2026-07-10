from django.http import HttpRequest
from inertia import share


class ShareUserDataMiddleware:
    """كود وسيط لمشاركة تفاصيل المستخدم الحالي مع واجهات Inertia بشكل آمن."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        # في بيئة Inertia، نقوم بنشر الحساب والمعلومات المشتركة في كل استجابة
        if request.user and request.user.is_authenticated:
            share(
                request,
                auth={
                    "user": {
                        "id": str(request.user.id),
                        "email": request.user.email,
                        "avatar_url": request.user.avatar_url or "",
                        "language": request.user.language,
                        "theme": request.user.theme,
                        "timezone": request.user.timezone,
                        "is_staff": request.user.is_staff,
                        "is_superuser": request.user.is_superuser,
                    }
                },
            )
        else:
            share(request, auth={"user": None})

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
