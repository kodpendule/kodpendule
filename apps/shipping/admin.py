from django.contrib import admin

from apps.shipping.models import City, ShippingMethod


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "shipping_price", "is_active", "sort_order")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("sort_order", "name")


@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "is_default")
    search_fields = ("name",)
