"""
Root URL configuration.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

import config.admin_branding  # noqa: F401 — Serbian admin site headers
from apps.core.admin_site import legacy_admin_redirect_patterns
from apps.core.admin_slugs import DASHBOARD_ADMIN_SLUG
from apps.core.sitemaps import sitemaps
from apps.core.storefront_urls import localized_path
from apps.core.views import robots_txt, set_shop_language

urlpatterns = [
    path("robots.txt", robots_txt, name="robots_txt"),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="sitemap",
    ),
    *legacy_admin_redirect_patterns(),
    path(f"admin/{DASHBOARD_ADMIN_SLUG}/", include("apps.dashboard.urls")),
    path("admin/", admin.site.urls),
    *localized_path("set_language", set_shop_language, sr="jezik/", en="language/"),
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
