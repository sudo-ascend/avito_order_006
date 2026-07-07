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
    existing_slugs = set(Page.objects.filter(slug__in=default_pages_by_slug()).values_list("slug", flat=True))
    for slug in default_pages_by_slug():
        if slug in existing_slugs:
            continue
        ensure_default_page(slug)


def ensure_default_page(slug: str) -> Page | None:
    definition = get_default_page_definition(slug)
    if not definition:
        return None

    page_defaults = _build_page_defaults(definition["page"])

    with transaction.atomic():
        page, created = Page.objects.get_or_create(slug=slug, defaults=page_defaults)
        if not page.advantage_group_id:
            page.advantage_group = _ensure_advantage_group(page, definition)
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


def _normalized_advantage_items(items: list[dict[str, Any]]) -> tuple[tuple[str, str, str, int], ...]:
    return tuple(
        (
            str(item.get("title") or "").strip(),
            str(item.get("description") or "").strip(),
            str(item.get("icon") or "check").strip(),
            int(item.get("order") or 10),
        )
        for item in items
    )


def _group_signature(group: AdvantageGroup) -> tuple[tuple[str, str, str, int], ...]:
    return tuple(
        group.advantages.order_by("order", "pk").values_list("title", "description", "icon", "order")
    )


def _ensure_advantage_group(page: Page, definition: dict[str, Any]) -> AdvantageGroup | None:
    items = definition.get("advantages") or []
    if not items:
        return None

    signature = _normalized_advantage_items(items)
    for group in AdvantageGroup.objects.prefetch_related("advantages"):
        if _group_signature(group) == signature:
            return group

    group = AdvantageGroup.objects.create(name=f"Преимущества: {page.name}")
    Advantage.objects.bulk_create([Advantage(group=group, **item) for item in items])
    return group


def _populate_related_content(page: Page, definition: dict[str, Any]) -> None:
    for key, model in RELATED_MODELS:
        items = definition.get(key) or []
        if items:
            model.objects.bulk_create([model(page=page, **item) for item in items])
