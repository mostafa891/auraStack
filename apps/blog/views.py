from django.shortcuts import get_object_or_404
from django.views import View
from inertia import render

from apps.blog.models import Post


class PostListView(View):
    def get(self, request):
        posts = Post.objects.filter(is_published=True)
        posts_data = [
            {
                "id": str(p.id),
                "title": p.title,
                "slug": p.slug,
                "summary": p.summary,
                "published_at": p.published_at.strftime("%Y-%m-%d"),
            }
            for p in posts
        ]
        return render(request, "Blog/Index", {"posts": posts_data})


class PostDetailView(View):
    def get(self, request, slug):
        post = get_object_or_404(Post, slug=slug, is_published=True)
        post_data = {
            "title": post.title,
            "slug": post.slug,
            "summary": post.summary,
            "content": post.content,
            "published_at": post.published_at.strftime("%Y-%m-%d"),
        }
        return render(request, "Blog/Detail", {"post": post_data})
