import math
import uuid

from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.utils.timezone import now


class Tag(models.Model):
    """وسوم تصنيف مقالات البلوغ."""

    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name, allow_unicode=True)
            if not base_slug:
                base_slug = f"tag-{uuid.uuid4().hex[:6]}"

            slug = base_slug
            counter = 1
            queryset = Tag.objects.all()
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)

            while queryset.filter(slug=slug).exists():
                max_len = 60 - len(str(counter)) - 1
                slug = f"{base_slug[:max_len]}-{counter}"
                counter += 1

            self.slug = slug
        super().save(*args, **kwargs)


class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    summary = models.TextField(max_length=500, blank=True)
    content = models.TextField(help_text="Markdown content supported")
    cover_image = models.ImageField(
        upload_to="blog/covers/", blank=True, null=True, help_text="صورة الغلاف للمقال"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="blog_posts",
        verbose_name="author",
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="posts", verbose_name="tags")
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(default=now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title, allow_unicode=True)
            if not base_slug:
                base_slug = f"post-{uuid.uuid4().hex[:6]}"

            slug = base_slug
            counter = 1
            queryset = Post.objects.all()
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)

            while queryset.filter(slug=slug).exists():
                max_len = 255 - len(str(counter)) - 1
                slug = f"{base_slug[:max_len]}-{counter}"
                counter += 1

            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def reading_time(self) -> int:
        """تقدير وقت القراءة بالدقائق (بمعدل 200 كلمة/دقيقة)."""
        words = len(self.content.split())
        minutes = math.ceil(words / 200)
        return max(1, minutes)
