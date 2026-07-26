import pytest
from django.urls import reverse

from apps.blog.models import Post


@pytest.fixture
def published_post(db):
    return Post.objects.create(
        title="Building SaaS with Django",
        summary="A comprehensive guide to building B2B SaaS.",
        content="This is the full article content in markdown format.",
        is_published=True,
    )


@pytest.mark.django_db
def test_post_slug_auto_generation():
    """Verifies automatic slug generation from post title on save."""
    post = Post.objects.create(title="My Brand New SaaS Feature", content="Content")
    assert post.slug == "my-brand-new-saas-feature"


@pytest.mark.django_db
def test_blog_post_list_view(client, published_post):
    """Verifies rendering published posts list view via Inertia."""
    response = client.get(reverse("blog:post_list"))
    assert response.status_code == 200

    # Verify post inclusion in Inertia page props
    posts_in_context = (
        response.context["page"]["props"]["posts"]
        if isinstance(response.context["page"], dict)
        else []
    )
    if not posts_in_context:
        import json

        page = response.context["page"]
        if isinstance(page, str):
            page = json.loads(page)
        posts_in_context = page["props"]["posts"]

    assert len(posts_in_context) == 1
    assert posts_in_context[0]["title"] == "Building SaaS with Django"


@pytest.mark.django_db
def test_blog_post_detail_view(client, published_post):
    """Verifies rendering individual blog post detail view."""
    response = client.get(reverse("blog:post_detail", kwargs={"slug": published_post.slug}))
    assert response.status_code == 200

    import json

    page = response.context["page"]
    if isinstance(page, str):
        page = json.loads(page)
    post_in_context = page["props"]["post"]

    assert post_in_context["title"] == "Building SaaS with Django"
    assert post_in_context["content"] == "This is the full article content in markdown format."
