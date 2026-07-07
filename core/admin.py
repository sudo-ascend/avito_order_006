from django.contrib import admin
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html

from core.models import Advantage, AdvantageGroup, Application, Equipment, Page, Service, SiteSettings, Step, WorkExample

admin.site.site_header = "Молния-Клининг"
admin.site.site_title = "Молния-Клининг"
admin.site.index_title = "Управление сайтом"


class OrderedInline(admin.StackedInline):
    extra = 0
    ordering = ("order", "pk")


class ServiceInline(OrderedInline):
    model = Service


class AdvantageInline(OrderedInline):
    model = Advantage


class WorkExampleInline(OrderedInline):
    model = WorkExample


class StepInline(OrderedInline):
    model = Step


class EquipmentInline(OrderedInline):
    model = Equipment


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "updated_at", "page_link")
    list_filter = ("is_active",)
    search_fields = ("name", "slug", "h1", "seo_title")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ServiceInline, WorkExampleInline, StepInline, EquipmentInline]
    fieldsets = (
        ("Основное", {"fields": ("name", "slug", "is_active", "h1", "eyebrow", "subtitle")}),
        ("SEO", {"fields": ("seo_title", "seo_description")}),
        (
            "Hero",
            {
                "fields": (
                    "hero_image",
                    "hero_image_alt",
                    "hero_advantages",
                    "right_card_items",
                    "cta_primary_text",
                    "cta_secondary_text",
                )
            },
        ),
        (
            "Заголовки секций",
            {
                "fields": (
                    "service_section_title",
                    "features_section_title",
                    "feature_items",
                    "work_examples_section_title",
                    "advantages_section_title",
                    "advantage_group",
                    "steps_section_title",
                    "equipment_section_title",
                    "about_section_title",
                    "guarantee_title",
                    "guarantee_text",
                    "guarantee_items",
                )
            },
        ),
    )

    def page_link(self, obj: Page):
        return format_html('<a href="{}" target="_blank" rel="noopener">Открыть</a>', obj.get_absolute_url())

    page_link.short_description = "Страница"


class SingletonAdmin(admin.ModelAdmin):
    def has_add_permission(self, request: HttpRequest) -> bool:
        return not self.model.objects.exists()

    def has_delete_permission(self, request: HttpRequest, obj=None) -> bool:
        return False

    def changelist_view(self, request: HttpRequest, extra_context=None):
        obj = self.model.objects.first()
        if obj:
            return redirect(reverse(f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_change", args=[obj.pk]))
        return redirect(reverse(f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_add"))


@admin.register(SiteSettings)
class SiteSettingsAdmin(SingletonAdmin):
    fieldsets = (
        ("Контакты", {"fields": ("phone", "email", "application_email", "address", "work_time")}),
        ("Брендинг", {"fields": ("logo", "favicon")}),
        ("Интеграции", {"fields": ("telegram_chat_id", "metrika_code")}),
        ("Дополнительно", {"fields": ("policy_text",)}),
    )


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "service", "page", "created_at")
    list_filter = ("page", "service", "created_at")
    search_fields = ("name", "phone", "service__title", "page__name", "page__slug", "comment")
    readonly_fields = ("name", "phone", "service", "page", "comment", "photo", "created_at")

    def add_view(self, request: HttpRequest, form_url: str = "", extra_context=None):
        extra_context = extra_context or {}
        extra_context["title"] = "Добавление заявки"
        return super().add_view(request, form_url, extra_context)


@admin.register(AdvantageGroup)
class AdvantageGroupAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    inlines = [AdvantageInline]
