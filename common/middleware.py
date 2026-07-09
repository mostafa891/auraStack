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

        response = self.get_response(request)
        return response
