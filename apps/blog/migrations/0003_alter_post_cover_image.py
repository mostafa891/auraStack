# Generated manually for help_text update

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0002_add_tag_author_cover"),
    ]

    operations = [
        migrations.AlterField(
            model_name="post",
            name="cover_image",
            field=models.ImageField(
                blank=True,
                help_text="Cover image for the article",
                null=True,
                upload_to="blog/covers/",
            ),
        ),
    ]
