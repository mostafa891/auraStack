from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """كلاس مجرد لتتبع التوقيت الصارم لجميع موديلات المنصة لمنع تكرار الحقول."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        return self.update(deleted_at=timezone.now())

    def hard_delete(self):
        return super().delete()


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).filter(deleted_at__isnull=True)


class SoftDeleteModel(models.Model):
    """موديل مجرد لدعم الحذف الناعم (Soft Delete) للملفات الحساسة."""

    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()  # جلب كافة السجلات بما فيها المحذوفة ناعماً

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])

    def hard_delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
