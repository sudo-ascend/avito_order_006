from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from django.db import transaction

from core.models import Advantage, AdvantageGroup, Equipment, Page, Service, Step

DEFAULT_PAGES_PATH = Path(__file__).resolve().parent / "data" / "default_pages.json"
MULTILINE_PAGE_FIELDS = ("hero_advantages", "feature_items", "guarantee_items")
RELATED_MODELS = (
    ("services", Service),
    ("steps", Step),
    ("equipment", Equipment),
)


@lru_cache(maxsize=1)
def load_default_pages() -> list[dict[str, Any]]:
    return json.loads(DEFAULT_PAGES_PATH.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def default_pages_by_slug() -> dict[str, dict[str, Any]]:
    return {item["slug"]: item for item in load_default_pages()}


def get_default_page_definition(slug: str) -> dict[str, Any] | None:
    return default_pages_by_slug().get(slug)


def ensure_default_pages() -> None:
    for slug in default_pages_by_slug():
        ensure_default_page(slug)


def ensure_default_page(slug: str) -> Page | None:
    definition = get_default_page_definition(slug)
    if not definition:
        return None

    page_defaults = _build_page_defaults(definition["page"])

    with transaction.atomic():
        page, created = Page.objects.get_or_create(slug=slug, defaults=page_defaults)
        advantage_group = _ensure_advantage_group(page, definition)
        if page.advantage_group_id != getattr(advantage_group, "pk", None):
            page.advantage_group = advantage_group
            page.save(update_fields=["advantage_group"])
        if created:
            _populate_related_content(page, definition)

    return page


def _build_page_defaults(page_data: dict[str, Any]) -> dict[str, Any]:
    defaults = dict(page_data)
    for field_name in MULTILINE_PAGE_FIELDS:
        defaults[field_name] = _join_lines(defaults.get(field_name))
    return defaults


def _join_lines(value: Any) -> str:
    if isinstance(value, list):
        return "\n".join(str(item).strip() for item in value if str(item).strip())
    if value is None:
        return ""
    return str(value)


def _ensure_advantage_group(page: Page, definition: dict[str, Any]) -> AdvantageGroup | None:
    items = definition.get("advantages") or []
    if not items:
        return None

    group_name = f"Преимущества: {page.name}"

    if page.advantage_group_id and not page.advantage_group.pages.exclude(pk=page.pk).exists():
        if page.advantage_group.name != group_name:
            page.advantage_group.name = group_name
            page.advantage_group.save(update_fields=["name"])
        return page.advantage_group

    source_items = items
    if page.advantage_group_id:
        source_items = list(
            page.advantage_group.advantages.order_by("order", "pk").values(
                "title",
                "description",
                "icon",
                "order",
            )
        )

    group = AdvantageGroup.objects.create(name=group_name)
    Advantage.objects.bulk_create([Advantage(group=group, **item) for item in source_items])
    return group


def _populate_related_content(page: Page, definition: dict[str, Any]) -> None:
    for key, model in RELATED_MODELS:
        items = definition.get(key) or []
        if items:
            model.objects.bulk_create([model(page=page, **item) for item in items])
