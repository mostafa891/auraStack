import django.conf
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0001_initial"),
        migrations.swappable_dependency(django.conf.settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Create Tag model
        migrations.CreateModel(
            name="Tag",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=50, unique=True)),
                ("slug", models.SlugField(blank=True, max_length=60, unique=True)),
            ],
            options={
                "verbose_name": "Tag",
                "verbose_name_plural": "Tags",
                "ordering": ["name"],
            },
        ),
        # Add cover_image field
        migrations.AddField(
            model_name="post",
            name="cover_image",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="blog/covers/",
                help_text="Cover image for the article",
            ),
        ),
        # Add author field
        migrations.AddField(
            model_name="post",
            name="author",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="blog_posts",
                to=django.conf.settings.AUTH_USER_MODEL,
                verbose_name="author",
            ),
        ),
        # Add tags ManyToMany relationship
        migrations.AddField(
            model_name="post",
            name="tags",
            field=models.ManyToManyField(
                blank=True,
                related_name="posts",
                to="blog.tag",
                verbose_name="tags",
            ),
        ),
    ]
