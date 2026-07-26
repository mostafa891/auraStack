import json


def get_request_data(request) -> dict:
    """Safely extracts request data from either JSON payload or Form-Encoded data
    for compatibility with Inertia and different content types."""
    if request.content_type and "application/json" in request.content_type:
        try:
            return json.loads(request.body)
        except json.JSONDecodeError:
            return {}
    return request.POST
