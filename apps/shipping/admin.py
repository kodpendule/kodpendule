from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.core.kp_admin import KPModelAdmin
from apps.shipping.models import City


@admin.register(City)
class CityAdmin(KPModelAdmin):
    list_display = ("name", "slug", "shipping_price", "is_active", "sort_order")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("sort_order", "name")
