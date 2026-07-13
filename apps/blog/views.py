from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.views import View
from inertia import render

from apps.blog.models import Post, Tag

POSTS_PER_PAGE = 10


class PostListView(View):
    def get(self, request):
        tag_slug = request.GET.get("tag", "")
        posts_qs = (
            Post.objects.filter(is_published=True).select_related("author").prefetch_related("tags")
        )

        if tag_slug:
            posts_qs = posts_qs.filter(tags__slug=tag_slug)

        paginator = Paginator(posts_qs, POSTS_PER_PAGE)
        page_number = request.GET.get("page", 1)
        page_obj = paginator.get_page(page_number)

        posts_data = [
            {
                "id": str(p.id),
                "title": p.title,
                "slug": p.slug,
                "summary": p.summary,
                "published_at": p.published_at.strftime("%Y-%m-%d"),
                "reading_time": p.reading_time,
                "cover_image": p.cover_image.url if p.cover_image else None,
                "author": p.author.get_full_name() or p.author.email if p.author else None,
                "tags": [{"name": t.name, "slug": t.slug} for t in p.tags.all()],
            }
            for p in page_obj
        ]

        all_tags = [{"name": t.name, "slug": t.slug} for t in Tag.objects.all()]

        return render(
            request,
            "Blog/Index",
            {
                "posts": posts_data,
                "tags": all_tags,
                "current_tag": tag_slug,
                "has_next": page_obj.has_next(),
                "has_previous": page_obj.has_previous(),
                "current_page": page_obj.number,
                "total_pages": paginator.num_pages,
            },
        )


class PostDetailView(View):
    def get(self, request, slug):
        post = get_object_or_404(
            Post.objects.select_related("author").prefetch_related("tags"),
            slug=slug,
            is_published=True,
        )
        post_data = {
            "title": post.title,
            "slug": post.slug,
            "summary": post.summary,
            "content": post.content,
            "published_at": post.published_at.strftime("%Y-%m-%d"),
            "reading_time": post.reading_time,
            "cover_image": post.cover_image.url if post.cover_image else None,
            "author": post.author.get_full_name() or post.author.email if post.author else None,
            "tags": [{"name": t.name, "slug": t.slug} for t in post.tags.all()],
        }
        return render(request, "Blog/Detail", {"post": post_data})
