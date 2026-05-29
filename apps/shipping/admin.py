from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.core.kp_admin import KPModelAdmin
from apps.shipping.models import City, ShippingMethod


@admin.register(City)
class CityAdmin(KPModelAdmin):
    list_display = ("name", "slug", "shipping_price", "is_active", "sort_order")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("sort_order", "name")


@admin.register(ShippingMethod)
class ShippingMethodAdmin(KPModelAdmin):
    list_display = ("name_sr", "name_en", "is_active", "is_default")
    list_filter = ("is_active", "is_default")
    search_fields = ("name_sr", "name_en", "description_sr", "description_en")
    fieldsets = (
        (
            _("Name & description"),
            {
                "fields": (
                    "name_sr",
                    "name_en",
                    "description_sr",
                    "description_en",
                ),
            },
        ),
        (
            None,
            {
                "fields": ("is_active", "is_default"),
            },
        ),
    )
