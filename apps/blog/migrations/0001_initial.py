import uuid

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Post",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("slug", models.SlugField(max_length=255, unique=True)),
                ("summary", models.TextField(blank=True, max_length=500)),
                ("content", models.TextField(help_text="Markdown content supported")),
                ("is_published", models.BooleanField(default=False)),
                ("published_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Blog Post",
                "verbose_name_plural": "Blog Posts",
                "ordering": ["-published_at", "-created_at"],
            },
        ),
    ]
