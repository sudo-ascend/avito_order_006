from django.db import migrations


def dedicate_advantage_groups(apps, schema_editor):
    Page = apps.get_model("core", "Page")
    Advantage = apps.get_model("core", "Advantage")
    AdvantageGroup = apps.get_model("core", "AdvantageGroup")

    for page in Page.objects.exclude(advantage_group_id=None).order_by("pk"):
        shared_pages = Page.objects.filter(advantage_group_id=page.advantage_group_id).exclude(pk=page.pk)
        if not shared_pages.exists():
            continue

        source_group = AdvantageGroup.objects.get(pk=page.advantage_group_id)
        new_group = AdvantageGroup.objects.create(name=f"Преимущества: {page.name}")
        advantages = list(
            Advantage.objects.filter(group_id=source_group.pk).order_by("order", "pk").values(
                "title",
                "description",
                "icon",
                "order",
            )
        )
        Advantage.objects.bulk_create([Advantage(group_id=new_group.pk, **item) for item in advantages])
        Page.objects.filter(pk=page.pk).update(advantage_group_id=new_group.pk)


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0003_remove_application_page_slug_application_page_and_more"),
    ]

    operations = [
        migrations.RunPython(dedicate_advantage_groups, migrations.RunPython.noop),
    ]
