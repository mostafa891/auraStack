from django.db import models


class TimeStampedModel(models.Model):
    """كلاس مجرد لتتبع التوقيت الصارم لجميع موديلات المنصة لمنع تكرار الحقول."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
