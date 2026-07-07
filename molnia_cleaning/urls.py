from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from core.sitemaps import PageSitemap

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sitemap.xml', sitemap, {'sitemaps': {'pages': PageSitemap}}, name='sitemap'),
    path('', include('core.urls')),
]

handler400 = 'core.views.error_400'
handler403 = 'core.views.error_403'
handler404 = 'core.views.error_404'
handler500 = 'core.views.error_500'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
