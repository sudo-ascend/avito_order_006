from django.db import migrations, models
import django.db.models.deletion


def migrate_advantages_to_groups(apps, schema_editor):
    Page = apps.get_model("core", "Page")
    Advantage = apps.get_model("core", "Advantage")
    AdvantageGroup = apps.get_model("core", "AdvantageGroup")

    group_ids_by_signature = {}

    for page in Page.objects.all().order_by("pk"):
        advantages = list(
            Advantage.objects.filter(page=page)
            .order_by("order", "pk")
            .values("pk", "title", "description", "icon", "order")
        )
        if not advantages:
            continue

        signature = tuple(
            (
                item["title"] or "",
                item["description"] or "",
                item["icon"] or "check",
                item["order"] or 10,
            )
            for item in advantages
        )
        group_id = group_ids_by_signature.get(signature)

        if group_id is None:
            group = AdvantageGroup.objects.create(name=f"Преимущества: {page.name}")
            group_id = group.pk
            group_ids_by_signature[signature] = group_id
            for item in advantages:
                Advantage.objects.filter(pk=item["pk"]).update(group_id=group_id)
        else:
            Advantage.objects.filter(pk__in=[item["pk"] for item in advantages]).delete()

        Page.objects.filter(pk=page.pk).update(advantage_group_id=group_id)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="AdvantageGroup",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255, verbose_name="Название группы")),
            ],
            options={
                "verbose_name": "Группа преимуществ",
                "verbose_name_plural": "Группы преимуществ",
                "ordering": ("name", "pk"),
            },
        ),
        migrations.AddField(
            model_name="page",
            name="advantage_group",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="pages",
                to="core.advantagegroup",
                verbose_name="Группа преимуществ",
            ),
        ),
        migrations.AddField(
            model_name="advantage",
            name="group",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="advantages",
                to="core.advantagegroup",
            ),
        ),
        migrations.RunPython(migrate_advantages_to_groups, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="advantage",
            name="page",
        ),
        migrations.AlterField(
            model_name="advantage",
            name="group",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="advantages",
                to="core.advantagegroup",
            ),
        ),
    ]
