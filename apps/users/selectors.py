from allauth.mfa.models import Authenticator
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers import registry

from apps.users.models import CustomUser


def get_user_by_email(email: str) -> CustomUser | None:
    """Retrieves a user model instance by email address."""
    try:
        return CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        return None


def is_totp_active(user) -> bool:
    """Checks whether 2FA/TOTP authentication is enabled for a user."""
    if not user or not user.is_authenticated:
        return False
    return Authenticator.objects.filter(user=user, type=Authenticator.Type.TOTP).exists()


def get_totp_authenticator(user) -> Authenticator | None:
    """Retrieves the active TOTP authenticator device instance for a user."""
    if not user or not user.is_authenticated:
        return None
    return Authenticator.objects.filter(user=user, type=Authenticator.Type.TOTP).first()


def list_user_social_accounts(user) -> list[SocialAccount]:
    """Lists all social accounts connected to a user profile."""
    if not user or not user.is_authenticated:
        return []
    return list(SocialAccount.objects.filter(user=user))


def list_social_providers() -> list[dict]:
    """Lists registered OAuth social login providers."""
    providers = []
    for provider_class in registry.get_class_list():
        providers.append(
            {
                "id": provider_class.id,
                "name": provider_class.name,
            }
        )
    return providers
