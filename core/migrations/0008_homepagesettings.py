from django.db import migrations, models
import django.db.models.deletion

import core.models


def create_home_page_settings(apps, schema_editor):
    Advantage = apps.get_model("core", "Advantage")
    AdvantageGroup = apps.get_model("core", "AdvantageGroup")
    HomePageSettings = apps.get_model("core", "HomePageSettings")

    group, _ = AdvantageGroup.objects.get_or_create(name="Главная страница")

    default_advantages = [
        (
            10,
            "Срочный выезд",
            "Оперативно подключаем бригаду и подбираем нужное оборудование под задачу.",
        ),
        (
            20,
            "Профильные работы",
            "Закрываем как бытовые, так и технически сложные объекты с нестандартными загрязнениями.",
        ),
        (
            30,
            "Прозрачная смета",
            "До начала работ фиксируем объём, этапы и ожидаемый результат.",
        ),
        (
            40,
            "Один подрядчик",
            "Не нужно собирать отдельных исполнителей на уборку, мойку, сушку и восстановление.",
        ),
    ]

    for order, title, description in default_advantages:
        Advantage.objects.get_or_create(
            group_id=group.pk,
            title=title,
            defaults={
                "order": order,
                "description": description,
                "icon": "check",
            },
        )

    settings, _ = HomePageSettings.objects.get_or_create(
        pk=1,
        defaults={
            "seo_title": "Молния-Клининг",
            "seo_description": (
                "Профессиональный клининг в Санкт-Петербурге: аварийная уборка, "
                "B2B-клининг, мойка окон и фасадов, сложные технические работы."
            ),
            "hero_image_alt": "Промышленная мойка окон и фасадов",
            "hero_title": "Профессиональный клининг для сложных объектов",
            "hero_text": (
                "Берём на себя аварийную уборку, очистку после пожара и потопа, "
                "B2B-клининг, мойку окон и фасадов, а также специализированные работы "
                "по восстановлению помещений."
            ),
            "hero_primary_text": "Связаться с нами",
            "hero_primary_link": "#contact",
            "hero_secondary_text": "Смотреть услуги",
            "hero_secondary_link": "#services",
            "hero_panel_items": (
                "Работаем 24/7\n"
                "Выезд по Санкт-Петербургу и области\n"
                "Полный цикл: от очистки до восстановления"
            ),
            "services_section_title": "Основные направления",
            "advantages_section_title": "Работаем аккуратно, быстро и без лишней бюрократии",
            "contact_section_title": "Контакты",
            "contact_phone_label": "Телефон",
            "contact_email_label": "Email",
            "contact_telegram_label": "Telegram",
            "contact_whatsapp_label": "WhatsApp",
            "contact_address_label": "Адрес",
            "contact_work_time_label": "Режим работы",
            "advantage_group_id": group.pk,
        },
    )

    if not settings.advantage_group_id:
        settings.advantage_group_id = group.pk
        settings.save(update_fields=["advantage_group"])


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0007_sitesettings_telegram_username_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="HomePageSettings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("seo_title", models.CharField(blank=True, max_length=255, verbose_name="SEO title главной")),
                ("seo_description", models.TextField(blank=True, verbose_name="SEO description главной")),
                (
                    "hero_image",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to=core.models.home_hero_image_upload_to,
                        verbose_name="Hero-изображение главной",
                    ),
                ),
                ("hero_image_alt", models.CharField(blank=True, max_length=255, verbose_name="Alt hero-изображения главной")),
                (
                    "hero_title",
                    models.CharField(
                        default="Профессиональный клининг для сложных объектов",
                        max_length=255,
                        verbose_name="Заголовок hero",
                    ),
                ),
                (
                    "hero_text",
                    models.TextField(
                        blank=True,
                        default=(
                            "Берём на себя аварийную уборку, очистку после пожара и потопа, "
                            "B2B-клининг, мойку окон и фасадов, а также специализированные "
                            "работы по восстановлению помещений."
                        ),
                        verbose_name="Текст hero",
                    ),
                ),
                (
                    "hero_primary_text",
                    models.CharField(default="Связаться с нами", max_length=120, verbose_name="Текст основной кнопки hero"),
                ),
                (
                    "hero_primary_link",
                    models.CharField(default="#contact", max_length=255, verbose_name="Ссылка основной кнопки hero"),
                ),
                (
                    "hero_secondary_text",
                    models.CharField(default="Смотреть услуги", max_length=120, verbose_name="Текст второй кнопки hero"),
                ),
                (
                    "hero_secondary_link",
                    models.CharField(default="#services", max_length=255, verbose_name="Ссылка второй кнопки hero"),
                ),
                (
                    "hero_panel_items",
                    models.TextField(
                        blank=True,
                        default=(
                            "Работаем 24/7\n"
                            "Выезд по Санкт-Петербургу и области\n"
                            "Полный цикл: от очистки до восстановления"
                        ),
                        verbose_name="Пункты правой карточки hero",
                    ),
                ),
                (
                    "services_section_title",
                    models.CharField(default="Основные направления", max_length=255, verbose_name="Заголовок секции направлений"),
                ),
                (
                    "advantages_section_title",
                    models.CharField(
                        default="Работаем аккуратно, быстро и без лишней бюрократии",
                        max_length=255,
                        verbose_name="Заголовок секции преимуществ",
                    ),
                ),
                ("contact_section_title", models.CharField(default="Контакты", max_length=255, verbose_name="Заголовок секции контактов")),
                ("contact_phone_label", models.CharField(default="Телефон", max_length=120, verbose_name="Подпись телефона")),
                ("contact_email_label", models.CharField(default="Email", max_length=120, verbose_name="Подпись email")),
                ("contact_telegram_label", models.CharField(default="Telegram", max_length=120, verbose_name="Подпись Telegram")),
                ("contact_whatsapp_label", models.CharField(default="WhatsApp", max_length=120, verbose_name="Подпись WhatsApp")),
                ("contact_address_label", models.CharField(default="Адрес", max_length=120, verbose_name="Подпись адреса")),
                (
                    "contact_work_time_label",
                    models.CharField(default="Режим работы", max_length=120, verbose_name="Подпись режима работы"),
                ),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Обновлено")),
                (
                    "advantage_group",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="home_pages",
                        to="core.advantagegroup",
                        verbose_name="Группа преимуществ главной",
                    ),
                ),
            ],
            options={
                "verbose_name": "Главная страница",
                "verbose_name_plural": "Главная страница",
            },
        ),
        migrations.RunPython(create_home_page_settings, migrations.RunPython.noop),
    ]
