import uuid

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _

from common.models import TimeStampedModel


class CustomUserManager(BaseUserManager):
    """Custom user manager where email is the unique identifier for authentication."""

    def create_user(self, email: str, password: str | None = None, **extra_fields):
        if not email:
            raise ValueError(_("The Email field must be set"))

        # Normalize domain casing and trim whitespace
        email = self.normalize_email(email.strip())
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str | None = None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser, TimeStampedModel):
    """Primary CustomUser model for the application."""

    class LanguageChoices(models.TextChoices):
        ENGLISH = "en", _("English")
        ARABIC = "ar", _("Arabic")

    class ThemeChoices(models.TextChoices):
        LIGHT = "LIGHT", _("Light")
        DARK = "DARK", _("Dark")
        SYSTEM = "SYSTEM", _("System")

    # Remove username field completely in favor of email authentication
    username = None

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Unique email address field with automatic database index
    email = models.EmailField(_("email address"), unique=True)

    # Avatar URL field supporting cloud/CDN hosted avatar images
    avatar_url = models.URLField(_("avatar URL"), max_length=500, null=True, blank=True)

    # User preferences fields
    language = models.CharField(
        max_length=2,
        choices=LanguageChoices.choices,
        default=LanguageChoices.ENGLISH,
    )
    theme = models.CharField(
        max_length=6,
        choices=ThemeChoices.choices,
        default=ThemeChoices.SYSTEM,
    )
    timezone = models.CharField(
        max_length=100,
        default="UTC",
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # Email is required by virtue of USERNAME_FIELD

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self) -> str:
        full_name = self.get_full_name().strip()
        return f"{full_name} <{self.email}>" if full_name else self.email
