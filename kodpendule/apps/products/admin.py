from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from parler.admin import TranslatableAdmin

from apps.core.slugs import localized_slug, unique_slug_for_translation
from apps.products.models import Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "alt_text", "sort_order")


@admin.register(Product)
class ProductAdmin(TranslatableAdmin):
    list_display = (
        "sku",
        "name",
        "slug_display",
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
            _("Name & description"),
            {
                "description": _(
                    "Fill in for the active language tab (Serbian / English). "
                    "Name is shown on the shop; slug is used in the URL."
                ),
                "fields": (
                    "name",
                    "slug",
                    "short_description",
                    "description",
                ),
            },
        ),
        (
            _("Pricing & stock"),
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
            _("SEO"),
            {
                "classes": ("collapse",),
                "fields": ("meta_title", "meta_description"),
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

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == "sku" and formfield:
            formfield.help_text = _(
                "Internal code (e.g. S1). Not the product title on the shop — use Name above."
            )
        return formfield

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("category")
            .prefetch_related("translations", "category__translations")
        )

    def save_translation(self, request, obj, form, change):
        translation = form.instance
        if not (translation.slug or "").strip():
            name = (translation.name or "").strip()
            if name:
                translation.slug = unique_slug_for_translation(
                    translation,
                    fallback=obj.sku,
                )
        super().save_translation(request, obj, form, change)

    @admin.display(description="Slug")
    def slug_display(self, obj: Product) -> str:
        slug = localized_slug(obj)
        if slug:
            return slug
        return format_html('<span style="color:#b45309;">{}</span>', _("missing — not on shop"))

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
