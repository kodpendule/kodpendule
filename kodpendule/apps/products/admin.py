from django.contrib import admin
from django.utils.html import format_html
from parler.admin import TranslatableAdmin

from apps.products.models import Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "alt_text", "sort_order")


@admin.register(Product)
class ProductAdmin(TranslatableAdmin):
    list_display = (
        "sku",
        "__str__",
        "category",
        "price_display",
        "stock_display",
        "is_active",
        "is_featured",
        "is_on_sale",
    )
    list_filter = (
        "is_active",
        "is_featured",
        "is_recommended",
        "is_on_sale",
        "category",
    )
    search_fields = ("sku", "translations__name", "translations__slug")
    list_select_related = ("category",)
    readonly_fields = ("created_at", "updated_at")
    inlines = [ProductImageInline]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "category",
                    "sku",
                    "price",
                    "discount_price",
                    "main_image",
                    "stock",
                    "minimum_stock_alert",
                ),
            },
        ),
        (
            "Visibility",
            {
                "fields": (
                    "is_active",
                    "is_featured",
                    "is_recommended",
                    "is_on_sale",
                ),
            },
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("category")
            .prefetch_related("translations", "category__translations")
        )

    @admin.display(description="Price")
    def price_display(self, obj: Product) -> str:
        if obj.has_discount:
            return format_html(
                '<span style="text-decoration:line-through;color:#888;">{}</span> {}',
                obj.price,
                obj.effective_price,
            )
        return str(obj.effective_price)

    @admin.display(description="Stock", ordering="stock")
    def stock_display(self, obj: Product) -> str:
        if obj.is_low_stock:
            return format_html(
                '<strong style="color:#b45309;">{} ⚠ low</strong>',
                obj.stock,
            )
        return str(obj.stock)
