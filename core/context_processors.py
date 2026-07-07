from core.default_pages import ensure_default_pages
from core.models import Page, SiteSettings


def site_context(request):
    ensure_default_pages()
    return {
        "site_settings": SiteSettings.objects.first(),
        "nav_pages": Page.objects.filter(is_active=True).only("slug", "name").order_by("pk"),
    }
