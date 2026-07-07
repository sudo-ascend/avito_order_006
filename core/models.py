from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any

from django.core.files.base import ContentFile
from django.db import models
from django.urls import reverse
from PIL import Image


def parse_text_items(value: str) -> list[str]:
    if not value:
        return []

    normalized = value.replace(",", "\n")
    return [item.strip(" -•\t") for item in normalized.splitlines() if item.strip()]


def parse_json_items(value: Any) -> list[dict[str, str]]:
    if not value:
        return []

    result: list[dict[str, str]] = []
    if isinstance(value, list):
        for item in value:
            if isinstance(item, str):
                result.append({"icon": "check", "text": item})
            elif isinstance(item, dict):
                result.append(
                    {
                        "icon": str(item.get("icon") or "check"),
                        "text": str(item.get("text") or item.get("title") or ""),
                    }
                )
    return [item for item in result if item["text"]]


def convert_field_to_webp(field_file: models.fields.files.FieldFile) -> None:
    if not field_file or not field_file.name:
        return
    if field_file.name.lower().endswith(".webp"):
        return

    field_file.open("rb")
    with Image.open(field_file) as image:
        image_format = "RGBA" if image.mode in {"RGBA", "LA", "P"} else "RGB"
        converted = image.convert(image_format)
        output = BytesIO()
        converted.save(output, format="WEBP", quality=84, optimize=True)

    output.seek(0)
    new_name = Path(field_file.name).with_suffix(".webp").as_posix()
    field_file.save(new_name, ContentFile(output.read()), save=False)


def hero_image_upload_to(instance: "Page", filename: str) -> str:
    return f"pages/{instance.slug}/hero/{Path(filename).name}"


def service_image_upload_to(instance: "Service", filename: str) -> str:
    return f"pages/{instance.page.slug}/services/{Path(filename).name}"


def before_work_example_upload_to(instance: "WorkExample", filename: str) -> str:
    return f"pages/{instance.page.slug}/work-examples/before-{Path(filename).name}"


def after_work_example_upload_to(instance: "WorkExample", filename: str) -> str:
    return f"pages/{instance.page.slug}/work-examples/after-{Path(filename).name}"


def equipment_image_upload_to(instance: "Equipment", filename: str) -> str:
    return f"pages/{instance.page.slug}/equipment/{Path(filename).name}"


def application_photo_upload_to(instance: "Application", filename: str) -> str:
    if instance.created_at:
        return f"applications/{instance.created_at:%Y/%m}/{Path(filename).name}"
    return f"applications/pending/{Path(filename).name}"


class WebPImageMixin(models.Model):
    image_fields: tuple[str, ...] = ()

    class Meta:
        abstract = True

    def save(self, *args: Any, **kwargs: Any) -> None:
        for field_name in self.image_fields:
            convert_field_to_webp(getattr(self, field_name))
        super().save(*args, **kwargs)


class SiteSettings(models.Model):
    phone = models.CharField("Телефон", max_length=32, blank=True)
    email = models.EmailField("Email", blank=True)
    application_email = models.EmailField(
        "Email для заявок",
        blank=True,
        default="molniya@profcleaning-comp.ru",
    )
    address = models.TextField("Адрес", blank=True)
    work_time = models.CharField("Режим работы", max_length=128, blank=True)
    metrika_code = models.TextField("Код Яндекс.Метрики", blank=True)
    policy_text = models.TextField("Текст политики", blank=True)
    telegram_chat_id = models.CharField("Telegram chat ID", max_length=128, blank=True)
    logo = models.ImageField("Логотип", upload_to="site/", blank=True, null=True)
    favicon = models.FileField("Favicon", upload_to="site/", blank=True, null=True)

    class Meta:
        verbose_name = "Настройки сайта"
        verbose_name_plural = "Настройки сайта"

    def __str__(self) -> str:
        return "Настройки сайта"

    @property
    def phone_href(self) -> str:
        digits = "".join(char for char in self.phone if char.isdigit())
        return f"tel:+{digits}" if digits else "tel:"


class AdvantageGroup(models.Model):
    name = models.CharField("Название группы", max_length=255)

    class Meta:
        verbose_name = "Группа преимуществ"
        verbose_name_plural = "Группы преимуществ"
        ordering = ("name", "pk")

    def __str__(self) -> str:
        return self.name


class Page(WebPImageMixin):
    slug = models.SlugField("Slug", unique=True, max_length=120)
    name = models.CharField("Название", max_length=255)
    h1 = models.CharField("H1", max_length=255)
    eyebrow = models.CharField("Короткий подзаголовок", max_length=255, blank=True)
    subtitle = models.TextField("Основной подзаголовок", blank=True)
    seo_title = models.CharField("SEO title", max_length=255, blank=True)
    seo_description = models.TextField("SEO description", blank=True)
    hero_image = models.ImageField("Hero-изображение", upload_to=hero_image_upload_to, blank=True, null=True)
    hero_image_alt = models.CharField("Alt hero-изображения", max_length=255, blank=True)
    hero_advantages = models.TextField("Преимущества в hero", blank=True)
    right_card_items = models.JSONField("Пункты правой карточки", blank=True, default=list)
    cta_primary_text = models.CharField("Текст основной кнопки", max_length=120, default="Вызвать бригаду")
    cta_secondary_text = models.CharField("Текст второй кнопки", max_length=120, default="Рассчитать стоимость")
    service_section_title = models.CharField("Заголовок секции услуг", max_length=255, default="Наши услуги")
    features_section_title = models.CharField("Заголовок секции действий", max_length=255, default="Что мы делаем")
    feature_items = models.TextField("Список действий", blank=True)
    work_examples_section_title = models.CharField("Заголовок секции работ", max_length=255, default="Наши работы")
    advantages_section_title = models.CharField("Заголовок секции преимуществ", max_length=255, default="Почему выбирают нас")
    advantage_group = models.ForeignKey(
        AdvantageGroup,
        on_delete=models.SET_NULL,
        related_name="pages",
        blank=True,
        null=True,
        verbose_name="Группа преимуществ",
    )
    steps_section_title = models.CharField("Заголовок секции этапов", max_length=255, default="Как мы работаем")
    equipment_section_title = models.CharField(
        "Заголовок секции оборудования",
        max_length=255,
        default="Наше профессиональное оборудование",
    )
    about_section_title = models.CharField("Заголовок секции о компании", max_length=255, default="О компании")
    guarantee_title = models.CharField(
        "Заголовок блока гарантии",
        max_length=255,
        default="Гарантия качества до 30 дней",
    )
    guarantee_text = models.TextField("Текст блока гарантии", blank=True)
    guarantee_items = models.TextField("Список гарантий", blank=True)
    is_active = models.BooleanField("Страница активна", default=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    image_fields = ("hero_image",)

    class Meta:
        verbose_name = "Страница"
        verbose_name_plural = "Страницы"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse("page_detail", kwargs={"slug": self.slug})

    @property
    def effective_seo_title(self) -> str:
        return self.seo_title or self.h1

    @property
    def hero_advantages_list(self) -> list[str]:
        return parse_text_items(self.hero_advantages)

    @property
    def right_card_list(self) -> list[dict[str, str]]:
        return parse_json_items(self.right_card_items)

    @property
    def feature_items_list(self) -> list[str]:
        return parse_text_items(self.feature_items)

    @property
    def guarantee_items_list(self) -> list[str]:
        return parse_text_items(self.guarantee_items)

    @property
    def advantages(self):
        if self.advantage_group_id:
            return self.advantage_group.advantages
        return Advantage.objects.none()


class OrderedPageItem(WebPImageMixin):
    page = models.ForeignKey(Page, on_delete=models.CASCADE)
    order = models.PositiveIntegerField("Порядок", default=10)

    class Meta:
        abstract = True
        ordering = ("order", "pk")


class Service(OrderedPageItem):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="services")
    title = models.CharField("Название", max_length=255)
    description = models.TextField("Описание", blank=True)
    image = models.ImageField("Изображение", upload_to=service_image_upload_to, blank=True, null=True)
    image_alt = models.CharField("Alt изображения", max_length=255, blank=True)
    icon = models.CharField("Иконка", max_length=64, blank=True, default="check")

    image_fields = ("image",)

    class Meta(OrderedPageItem.Meta):
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"

    def __str__(self) -> str:
        return self.title


class Advantage(models.Model):
    group = models.ForeignKey(AdvantageGroup, on_delete=models.CASCADE, related_name="advantages")
    order = models.PositiveIntegerField("Порядок", default=10)
    title = models.CharField("Название", max_length=255)
    description = models.TextField("Описание", blank=True)
    icon = models.CharField("Иконка", max_length=64, blank=True, default="check")

    class Meta:
        verbose_name = "Преимущество"
        verbose_name_plural = "Преимущества"
        ordering = ("order", "pk")

    def __str__(self) -> str:
        return self.title


class WorkExample(OrderedPageItem):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="work_examples")
    before_image = models.ImageField("Фото до", upload_to=before_work_example_upload_to, blank=True, null=True)
    before_alt = models.CharField("Alt для фото до", max_length=255, blank=True)
    after_image = models.ImageField("Фото после", upload_to=after_work_example_upload_to, blank=True, null=True)
    after_alt = models.CharField("Alt для фото после", max_length=255, blank=True)
    description = models.TextField("Описание", blank=True)

    image_fields = ("before_image", "after_image")

    class Meta(OrderedPageItem.Meta):
        verbose_name = "Пример работы"
        verbose_name_plural = "Примеры работ"

    def __str__(self) -> str:
        return self.description[:50] or f"Пример #{self.pk}"


class Step(OrderedPageItem):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="steps")
    title = models.CharField("Название", max_length=255)
    description = models.TextField("Описание", blank=True)
    icon = models.CharField("Иконка", max_length=64, blank=True, default="check")

    class Meta(OrderedPageItem.Meta):
        verbose_name = "Этап"
        verbose_name_plural = "Этапы"

    def __str__(self) -> str:
        return self.title


class Equipment(OrderedPageItem):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="equipment")
    title = models.CharField("Название", max_length=255)
    description = models.TextField("Описание", blank=True)
    image = models.ImageField("Изображение", upload_to=equipment_image_upload_to, blank=True, null=True)
    image_alt = models.CharField("Alt изображения", max_length=255, blank=True)

    image_fields = ("image",)

    class Meta(OrderedPageItem.Meta):
        verbose_name = "Оборудование"
        verbose_name_plural = "Оборудование"

    def __str__(self) -> str:
        return self.title


class Application(WebPImageMixin):
    name = models.CharField("Имя", max_length=255)
    phone = models.CharField("Телефон", max_length=32)
    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        related_name="applications",
        verbose_name="Услуга",
        blank=True,
        null=True,
    )
    page = models.ForeignKey(
        Page,
        on_delete=models.PROTECT,
        related_name="applications",
        verbose_name="Страница-источник",
        blank=True,
        null=True,
    )
    comment = models.TextField("Комментарий", blank=True)
    photo = models.ImageField("Фото", upload_to=application_photo_upload_to, blank=True, null=True)
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    image_fields = ("photo",)

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ("-created_at",)

    @property
    def service_title(self) -> str:
        return self.service.title if self.service_id else ""

    @property
    def page_slug(self) -> str:
        return self.page.slug if self.page_id else ""

    def __str__(self) -> str:
        service_title = self.service_title or "Без услуги"
        return f"{self.name} — {service_title}"
