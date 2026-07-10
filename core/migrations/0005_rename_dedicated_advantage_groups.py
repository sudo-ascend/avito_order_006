from django.db import migrations


def rename_dedicated_advantage_groups(apps, schema_editor):
    Page = apps.get_model("core", "Page")
    AdvantageGroup = apps.get_model("core", "AdvantageGroup")

    for page in Page.objects.exclude(advantage_group_id=None).order_by("pk"):
        expected_name = f"Преимущества: {page.name}"
        AdvantageGroup.objects.filter(pk=page.advantage_group_id).update(name=expected_name)


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0004_dedicate_advantage_groups"),
    ]

    operations = [
        migrations.RunPython(rename_dedicated_advantage_groups, migrations.RunPython.noop),
    ]
