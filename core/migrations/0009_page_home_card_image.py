from django.db import migrations, models

import core.models


def copy_hero_images_to_home_cards(apps, schema_editor):
    Page = apps.get_model("core", "Page")
    for page in Page.objects.all():
        changed = False
        if page.hero_image and not page.home_card_image:
            page.home_card_image = page.hero_image
            changed = True
        if page.hero_image_alt and not page.home_card_image_alt:
            page.home_card_image_alt = page.hero_image_alt
            changed = True
        if changed:
            page.save(update_fields=["home_card_image", "home_card_image_alt"])


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0008_homepagesettings"),
    ]

    operations = [
        migrations.AddField(
            model_name="page",
            name="home_card_image",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to=core.models.home_card_image_upload_to,
                verbose_name="Изображение карточки на главной",
            ),
        ),
        migrations.AddField(
            model_name="page",
            name="home_card_image_alt",
            field=models.CharField(
                blank=True,
                max_length=255,
                verbose_name="Alt изображения карточки на главной",
            ),
        ),
        migrations.RunPython(copy_hero_images_to_home_cards, migrations.RunPython.noop),
    ]
