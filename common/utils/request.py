import json


def get_request_data(request) -> dict:
    """استخراج بيانات الطلب سواء كانت JSON أو Form-Encoded بأمان
    لتوافق Inertia والترميزات المختلفة."""
    if request.content_type and "application/json" in request.content_type:
        try:
            return json.loads(request.body)
        except json.JSONDecodeError:
            return {}
    return request.POST
