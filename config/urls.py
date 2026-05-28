"""
Root URL configuration.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.i18n import set_language

import config.admin_branding  # noqa: F401 — Serbian admin site headers
from apps.core.sitemaps import sitemaps
from apps.core.views import robots_txt

urlpatterns = [
    path("robots.txt", robots_txt, name="robots_txt"),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="sitemap",
    ),
    path("admin/dashboard/", include("apps.dashboard.urls")),
    path("admin/", admin.site.urls),
    path("jezik/", set_language, name="set_language"),
    path("", include("apps.core.urls")),
    path("", include("apps.categories.urls")),
    path("", include("apps.products.urls")),
    path("", include("apps.cart.urls")),
    path("", include("apps.checkout.urls")),
    path("", include("apps.orders.urls")),
    path("", include("apps.accounts.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    try:
        import debug_toolbar  # noqa: F401

        urlpatterns = [
            path("__debug__/", include("debug_toolbar.urls")),
            *urlpatterns,
        ]
    except ImportError:
        pass
