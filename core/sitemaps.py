from django.contrib.sitemaps import Sitemap

from core.models import Page


class PageSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Page.objects.filter(is_active=True).order_by("slug")

    def lastmod(self, obj: Page):
        return obj.updated_at
