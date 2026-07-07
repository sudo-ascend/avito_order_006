from __future__ import annotations

from pathlib import Path

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.default_pages import ensure_default_pages
from core.models import Page, SiteSettings

ASSETS_DIR = Path(__file__).resolve().parents[3] / "assets" / "images"

SITE_SETTINGS_DEFAULTS = {
    "phone": "+7 921 947 80 89",
    "email": "molniya@profcleaning-comp.ru",
    "address": "194017, г. Санкт-Петербург, пр-т Энгельса, д. 54",
    "work_time": "Работаем 24/7",
}

PAGE_ASSETS = {
    "uborka-posle-potopa": {
        "hero": "flood-hero.webp",
        "services": [
            "svc-flood-emergency.webp",
            "svc-eq-airmover.webp",
            "svc-flood-disinfection.webp",
            "svc-flood-restore.webp",
            "svc-flood-insurance.webp",
        ],
        "equipment": [
            "eq-flood-pumps.webp",
            "svc-eq-dehumidifier.webp",
            "svc-flood-drying.webp",
            "svc-eq-wet-vacuum.webp",
            "svc-eq-generator-mobile.webp",
            "svc-eq-meter-thermal.webp",
        ],
    },
    "uborka-posle-pozhara": {
        "hero": "fire-hero.webp",
        "services": [
            "svc-fire-soot.webp",
            "svc-fire-surface.webp",
            "svc-fire-odor.webp",
            "svc-fire-disposal.webp",
            "svc-fire-insurance.webp",
        ],
        "equipment": [
            "equipment-vacuum.webp",
            "eq-fire-ozone.webp",
            "eq-fire-steamer.webp",
            "equipment-sprayer.webp",
            "svc-eq-airmover.webp",
            "equipment-chemistry.webp",
        ],
    },
    "uborka-posle-smerti": {
        "hero": "death-hero.webp",
        "services": [
            "svc-death-disinfect.webp",
            "svc-death-bio.webp",
            "svc-death-odor.webp",
            "svc-death-ozone.webp",
            "svc-death-disposal.webp",
            "svc-death-restore.webp",
        ],
        "equipment": [
            "eq-death-ozone.webp",
            "equipment-sprayer.webp",
            "equipment-vacuum.webp",
            "eq-death-steamer.webp",
            "equipment-chemistry.webp",
            "equipment-ppe.webp",
        ],
    },
    "uborka-posle-remonta": {
        "hero": "renovation-card.webp",
        "services": [
            "svc-renovation-dust.webp",
            "svc-repair-surface.webp",
            "svc-repair-window.webp",
            "svc-repair-turnkey.webp",
            "svc-repair-debris.webp",
        ],
        "equipment": [
            "svc-eq-wet-vacuum.webp",
            "svc-eq-floor-scrubber.webp",
            "eq-repair-pressure.webp",
            "equipment-floor-machine.webp",
            "equipment-chemistry.webp",
            "eq-repair-inventory.webp",
        ],
    },
    "b2b-cleaning": {
        "hero": "svc-b2b-hero.webp",
        "services": [
            "svc-b2b-office.webp",
            "svc-b2b-warehouse.webp",
            "svc-window-hand.webp",
            "svc-b2b-commercial.webp",
            "svc-b2b-once.webp",
        ],
        "equipment": [
            "svc-eq-floor-scrubber.webp",
            "svc-eq-wet-vacuum.webp",
            "equipment-sprayer.webp",
            "equipment-chemistry.webp",
            "svc-window-hand.webp",
            "svc-repair-surface.webp",
        ],
    },
    "myte-okon-i-fasadov": {
        "hero": "svc-window-hero.webp",
        "services": [
            "svc-window-alpinism.webp",
            "svc-window-lift.webp",
            "svc-window-wfp.webp",
            "svc-window-hand.webp",
        ],
        "equipment": [
            "svc-eq-wfp-backpack.webp",
            "svc-eq-wfp-system.webp",
            "svc-window-lift.webp",
            "svc-window-alpinism.webp",
            "svc-eq-window-kit.webp",
        ],
    },
    "gidropeskostruynaya-ochistka": {
        "hero": "hydro-hero.webp",
        "services": [
            "svc-hydro-graffiti.webp",
            "svc-eq-pressure-washer.webp",
            "svc-hydro-paint.webp",
            "hydro-hero.webp",
            "hydro-card.webp",
            "svc-hydro-stone.webp",
        ],
        "equipment": [
            "svc-eq-pressure-washer.webp",
            "svc-eq-ibc.webp",
            "svc-eq-diesel-generator.webp",
            "svc-eq-abrasive.webp",
            "svc-eq-nozzle.webp",
            "equipment-ppe.webp",
        ],
    },
}


def save_asset(field_file, asset_name: str) -> None:
    source_path = ASSETS_DIR / asset_name
    if not source_path.exists():
        raise CommandError(f"Файл не найден: {source_path}")

    if field_file.name:
        field_file.delete(save=False)
    field_file.save(source_path.name, ContentFile(source_path.read_bytes()), save=False)


def sync_ordered_images(items, asset_names: list[str]) -> None:
    if len(items) != len(asset_names):
        raise CommandError(
            f"Количество объектов ({len(items)}) не совпадает с количеством картинок ({len(asset_names)})."
        )

    for item, asset_name in zip(items, asset_names, strict=True):
        save_asset(item.image, asset_name)
        if not item.image_alt:
            item.image_alt = item.title
        item.save()


class Command(BaseCommand):
    help = "Заполняет БД контентом и изображениями из каталога assets."

    @transaction.atomic
    def handle(self, *args, **options):
        ensure_default_pages()

        site_settings, _ = SiteSettings.objects.get_or_create()
        for field_name, value in SITE_SETTINGS_DEFAULTS.items():
            if not getattr(site_settings, field_name):
                setattr(site_settings, field_name, value)
        site_settings.save()

        for slug, assets in PAGE_ASSETS.items():
            page = Page.objects.get(slug=slug)
            save_asset(page.hero_image, assets["hero"])
            page.hero_image_alt = page.h1
            page.save()

            sync_ordered_images(list(page.services.order_by("order", "pk")), assets["services"])
            sync_ordered_images(list(page.equipment.order_by("order", "pk")), assets["equipment"])

        self.stdout.write(self.style.SUCCESS("Контент и изображения синхронизированы с БД."))
