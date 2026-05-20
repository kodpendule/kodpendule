"""
Root URL configuration.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.i18n import set_language

urlpatterns = [
    path("admin/", admin.site.urls),
    path("jezik/", set_language, name="set_language"),
    path("", include("apps.core.urls")),
    path("", include("apps.categories.urls")),
    path("", include("apps.products.urls")),
    path("", include("apps.accounts.urls")),
    # path("admin/dashboard/", include("apps.dashboard.urls")),
    # path("api/v1/", include("config.api.urls")),
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

# Step 9: wrap storefront URLs with i18n_patterns()
