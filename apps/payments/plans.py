from django.utils.translation import gettext_lazy as _

PLANS = {
    "free": {
        "name": _("Free Plan"),
        "max_members": 3,
        "features": ["basic_tools"],
        "ai_tokens": 1000,
    },
    "pro": {
        "name": _("Pro Plan"),
        "max_members": 20,
        "features": ["basic_tools", "advanced_analytics", "ai_features"],
        "ai_tokens": 100000,
    },
}
