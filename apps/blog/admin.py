from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.blog.models import Post


@admin.register(Post)
class PostAdmin(ModelAdmin):
    list_display = ("title", "is_published", "published_at", "created_at")
    list_filter = ("is_published", "created_at")
    search_fields = ("title", "content", "summary")
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        (None, {"fields": ("title", "slug", "summary", "content", "is_published", "published_at")}),
    )
