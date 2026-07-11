from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.conf import settings
from django.urls import include, path, re_path
from django.views.static import serve

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

# Media files are stored on the local filesystem in this project, so keep them
# available even when DEBUG is disabled in the local environment.
urlpatterns += [
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]
