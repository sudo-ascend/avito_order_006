from django import template
from django.utils.safestring import mark_safe

from core.utils import phone_href

register = template.Library()

ICON_PATHS = {
    "phone": '<path d="M6.6 3.8 4.9 5.5c-.6.6-.7 1.5-.3 2.3 2 3.8 4.9 6.7 8.7 8.7.8.4 1.7.3 2.3-.3l1.7-1.7-3.2-3.2-1.5 1.5c-1.8-.9-3.1-2.2-4-4l1.3-1.8-3.3-3.2Z"/>',
    "clock": '<path d="M12 4a8 8 0 1 0 0 16 8 8 0 0 0 0-16Zm0 4v4l3 2"/>',
    "time": '<path d="M12 3v3m0 12v3M3 12h3m12 0h3M5.6 5.6l2.1 2.1m8.6 8.6 2.1 2.1M18.4 5.6l-2.1 2.1m-8.6 8.6-2.1 2.1"/>',
    "truck": '<path d="M3 7h10v8H3V7Zm10 3h4l3 3v2h-7v-5ZM6 18a2 2 0 1 0 0-4 2 2 0 0 0 0 4Zm11 0a2 2 0 1 0 0-4 2 2 0 0 0 0 4Z"/>',
    "shield": '<path d="M12 3 5 6v5c0 4.5 3 7.9 7 9.5 4-1.6 7-5 7-9.5V6l-7-3Zm-3 9 2 2 4-5"/>',
    "check": '<path d="m6 12 4 4 8-9"/><path d="M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18Z"/>',
    "leaf": '<path d="M20 4c-7 0-12 3.5-13 9-.4 2 .2 4.1 1.7 5.6C14 17.7 18 13.7 20 4Z"/><path d="M4 20c3-5 7-8 12-10"/>',
    "document": '<path d="M7 3h7l4 4v14H7V3Zm7 0v5h4M9 12h6M9 16h6"/>',
    "spray": '<path d="M7 7h6v4H7V7Zm2 4v8h5v-4l2-2v-2H9Zm8-6 3-2M18 9h3M18 13l3 2"/>',
    "home": '<path d="M4 11 12 4l8 7v9h-5v-6H9v6H4v-9Z"/>',
    "water": '<path d="M12 3s6 6.4 6 10.4A6 6 0 0 1 6 13.4C6 9.4 12 3 12 3Z"/>',
    "message": '<path d="M4 5h16v11H8l-4 4V5Z"/>',
    "calculator": '<path d="M7 3h10v18H7V3Zm2 3h6v3H9V6Zm0 6h2m2 0h2M9 16h2m2 0h2"/>',
    "user-check": '<path d="M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8Zm-6 9c.8-3.4 3-5 6-5 1.1 0 2.1.2 3 .6M14 17l2 2 5-6"/>',
}


@register.simple_tag
def render_icon(name="check"):
    path = ICON_PATHS.get(name, ICON_PATHS["check"])
    return mark_safe(f'<svg class="icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false">{path}</svg>')


@register.filter
def tel_href(phone):
    return phone_href(phone)
