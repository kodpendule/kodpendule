"""
Root URL configuration.

Step 3+: admin, i18n storefront, sitemap, robots, API includes.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # path("admin/dashboard/", include("apps.dashboard.urls")),
    # path("api/v1/", include("config.api.urls")),
    # path("", include("apps.core.urls")),
]

# Step 9: wrap storefront with i18n_patterns()
