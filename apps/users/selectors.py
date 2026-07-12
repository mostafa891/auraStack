from allauth.mfa.models import Authenticator
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers import registry

from apps.users.models import CustomUser


def get_user_by_email(email: str) -> CustomUser | None:
    """جلب مستخدم عن طريق بريده الإلكتروني."""
    try:
        return CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        return None


def is_totp_active(user) -> bool:
    """التحقق مما إذا كانت المصادقة الثنائية (2FA/TOTP) مفعلة للمستخدم."""
    if not user or not user.is_authenticated:
        return False
    return Authenticator.objects.filter(user=user, type=Authenticator.Type.TOTP).exists()


def get_totp_authenticator(user) -> Authenticator | None:
    """جلب جهاز المصادقة الثنائية النشط للمستخدم."""
    if not user or not user.is_authenticated:
        return None
    return Authenticator.objects.filter(user=user, type=Authenticator.Type.TOTP).first()


def list_user_social_accounts(user) -> list[SocialAccount]:
    """جلب قائمة الحسابات الاجتماعية المرتبطة بحساب المستخدم."""
    if not user or not user.is_authenticated:
        return []
    return list(SocialAccount.objects.filter(user=user))


def list_social_providers() -> list[dict]:
    """جلب قائمة بكل مزودي تسجيل الدخول الاجتماعي المسجلين في المنصة."""
    providers = []
    for provider_class in registry.get_class_list():
        providers.append(
            {
                "id": provider_class.id,
                "name": provider_class.name,
            }
        )
    return providers
