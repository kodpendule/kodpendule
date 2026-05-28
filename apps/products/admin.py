from decimal import Decimal, ROUND_HALF_UP

from django import forms
from django.contrib import admin, messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils.translation import gettext_lazy as _
from parler.admin import TranslatableAdmin

from apps.core.admin_display import price_cell, slug_warning_cell, stock_cell
from apps.core.slugs import localized_slug, unique_slug_for_translation
from apps.products.models import Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    verbose_name = _("Gallery image")
    verbose_name_plural = _("Gallery images")
    fields = ("image", "alt_text", "sort_order")
    classes = ("kp-inline-gallery",)


class PromoSaleForm(forms.Form):
    products = forms.ModelMultipleChoiceField(
        label=_("Products"),
        queryset=Product.objects.order_by("-updated_at"),
        widget=forms.SelectMultiple(attrs={"size": "14"}),
    )
    discount_percent = forms.DecimalField(
        label=_("Discount percent"),
        min_value=Decimal("0.01"),
        max_value=Decimal("95"),
        decimal_places=2,
        help_text=_("Example: 15 means 15% discount from regular price."),
    )


_PRODUCT_FIELDSETS = (
    (
        _("Name & description"),
        {
            "classes": ("kp-fieldset", "kp-fieldset--product-copy"),
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
            "classes": ("kp-fieldset", "kp-fieldset--pricing"),
            "description": _(
                "Set price and stock here. When stock is at or below the alert level, "
                "the product appears in analytics low-stock warnings."
            ),
            "fields": (
                "category",
                "sku",
                "price",
                "main_image",
                "stock",
                "minimum_stock_alert",
            ),
        },
    ),
    (
        _("SEO"),
        {
            "classes": ("collapse", "kp-fieldset", "kp-fieldset--seo"),
            "description": _("Optional — used by search engines."),
            "fields": ("meta_title", "meta_description"),
        },
    ),
)


@admin.register(Product)
class ProductAdmin(TranslatableAdmin):
    change_list_template = "admin/products/product/change_list.html"
    list_display = (
        "sku",
        "name",
        "slug_display",
        "category",
        "price_display",
        "stock_display",
    )
    search_fields = ("sku", "translations__name", "translations__slug")
    list_select_related = ("category",)
    inlines = [ProductImageInline]
    list_per_page = 25
    save_on_top = True

    def get_fieldsets(self, request, obj=None):
        fieldsets = list(_PRODUCT_FIELDSETS)
        if obj is not None:
            fieldsets.append(
                (
                    _("Timestamps"),
                    {
                        "fields": ("created_at", "updated_at"),
                        "classes": ("collapse",),
                    },
                ),
            )
        return fieldsets

    def get_readonly_fields(self, request, obj=None):
        if obj is not None:
            return ("created_at", "updated_at")
        return ()

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if not formfield:
            return formfield
        help_map = {
            "sku": _(
                "Internal code (e.g. S1). Not the product title on the shop — use Name above."
            ),
            "stock": _("Units available to sell."),
            "minimum_stock_alert": _(
                "Show a low-stock warning at or below this quantity."
            ),
        }
        if db_field.name in help_map:
            formfield.help_text = help_map[db_field.name]
        return formfield

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("category")
            .prefetch_related("translations", "category__translations")
        )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "promo-sales/",
                self.admin_site.admin_view(self.promo_sales_view),
                name="products_product_promo_sales",
            ),
            path(
                "recommended/",
                self.admin_site.admin_view(self.recommended_products_view),
                name="products_product_recommended",
            ),
        ]
        return custom_urls + urls

    def _product_admin_queryset(self, request):
        return (
            Product.objects.all()
            .select_related("category")
            .prefetch_related("translations", "category__translations")
            .order_by("-updated_at")
        )

    def recommended_products_view(self, request: HttpRequest) -> HttpResponse:
        if not self.has_change_permission(request):
            return redirect("admin:index")

        product_qs = self._product_admin_queryset(request)
        if request.method == "POST":
            selected_ids = request.POST.getlist("recommended")
            try:
                selected_pks = [int(pk) for pk in selected_ids]
            except ValueError:
                selected_pks = []

            Product.objects.update(is_recommended=False, recommended_order=0)
            if selected_pks:
                products_by_pk = {
                    p.pk: p for p in product_qs.filter(pk__in=selected_pks)
                }
                for order, pk in enumerate(selected_pks):
                    product = products_by_pk.get(pk)
                    if not product:
                        continue
                    product.is_recommended = True
                    product.recommended_order = order
                    product.save(
                        update_fields=["is_recommended", "recommended_order", "updated_at"]
                    )

            messages.success(
                request,
                _("Recommended products updated (%(count)s selected).")
                % {"count": len(selected_pks)},
            )
            return redirect(reverse("admin:products_product_recommended"))

        products = list(product_qs)
        context = {
            **self.admin_site.each_context(request),
            "opts": self.model._meta,
            "title": _("Recommended products"),
            "products": products,
            "selected_ids": {p.pk for p in products if p.is_recommended},
        }
        return render(request, "admin/products/product/recommended_products.html", context)

    def promo_sales_view(self, request: HttpRequest) -> HttpResponse:
        if not self.has_change_permission(request):
            return redirect("admin:index")

        form = PromoSaleForm(request.POST or None)
        if request.method == "POST" and form.is_valid():
            selected_products = form.cleaned_data["products"]
            percent = form.cleaned_data["discount_percent"]
            multiplier = (Decimal("100") - percent) / Decimal("100")

            updated = 0
            skipped = 0
            for product in selected_products:
                new_price = (product.price * multiplier).quantize(
                    Decimal("0.01"),
                    rounding=ROUND_HALF_UP,
                )

                if new_price >= product.price:
                    skipped += 1
                    continue

                product.discount_price = new_price
                product.save(update_fields=["discount_price", "updated_at"])
                updated += 1

            if updated:
                messages.success(
                    request,
                    _("Promo sale updated for %(count)s products.")
                    % {"count": updated},
                )
            if skipped:
                messages.warning(
                    request,
                    _(
                        "%(count)s products skipped because promo price was not lower than regular price."
                    )
                    % {"count": skipped},
                )
            return redirect(reverse("admin:products_product_changelist"))

        context = {
            **self.admin_site.each_context(request),
            "opts": self.model._meta,
            "title": _("Promo sales"),
            "form": form,
        }
        return render(request, "admin/products/product/promo_sales.html", context)

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

    @admin.display(description=_("Slug"))
    def slug_display(self, obj: Product) -> str:
        return slug_warning_cell(localized_slug(obj))

    @admin.display(description=_("Price"), ordering="price")
    def price_display(self, obj: Product) -> str:
        return price_cell(
            obj.effective_price,
            base=obj.price,
            has_discount=obj.has_discount,
        )

    @admin.display(description=_("Stock"), ordering="stock")
    def stock_display(self, obj: Product) -> str:
        return stock_cell(
            obj.stock,
            is_low=obj.is_low_stock,
            alert_at=obj.minimum_stock_alert,
        )
