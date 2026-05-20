from django.conf import settings
from django.http import Http404
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView

from apps.categories.selectors import get_category_by_slug
from apps.core.breadcrumbs import categories_crumb, home_crumb, products_crumb
from apps.core.mixins import ShopLanguageMixin
from apps.core.templatetags.shop_tags import product_meta_title
from apps.products.models import Product
from apps.products.selectors import (
    active_products_qs,
    filter_products_by_category,
    get_product_by_slug,
    related_products,
    search_products,
)


class ProductListView(ShopLanguageMixin, ListView):
    template_name = "products/list.html"
    context_object_name = "products"
    paginate_by = settings.SHOP_PRODUCTS_PER_PAGE

    def get_queryset(self):
        qs = active_products_qs(self.shop_language)
        query = self.request.GET.get("q", "").strip()
        category_slug = self.request.GET.get("kategorija", "").strip()

        if query:
            qs = search_products(query, self.shop_language)
        if category_slug:
            category = get_category_by_slug(category_slug, self.shop_language)
            if category:
                qs = filter_products_by_category(
                    category,
                    self.shop_language,
                    include_children=True,
                )
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("q", "").strip()
        category_slug = self.request.GET.get("kategorija", "").strip()
        active_category = None
        if category_slug:
            active_category = get_category_by_slug(category_slug, self.shop_language)

        if query:
            meta_title = _("Search results for “%(query)s”") % {"query": query}
        elif active_category:
            meta_title = active_category.name
        else:
            meta_title = _("Products")

        breadcrumbs = [home_crumb(), products_crumb()]
        if active_category:
            breadcrumbs = [home_crumb(), categories_crumb(), (active_category.name, None)]
        elif query:
            breadcrumbs = [home_crumb(), products_crumb(), (_("Search"), None)]

        context.update(
            {
                "search_query": query,
                "active_category": active_category,
                "breadcrumb_items": breadcrumbs,
                "meta_title": meta_title,
                "meta_description": _("Browse our product catalog."),
                "canonical_url": self.request.build_absolute_uri(
                    self.request.path
                ),
            }
        )
        return context


class ProductDetailView(ShopLanguageMixin, DetailView):
    template_name = "products/detail.html"
    context_object_name = "product"

    def get_object(self, queryset=None):
        product = get_product_by_slug(self.kwargs["slug"], self.shop_language)
        if product is None:
            raise Http404(_("Product not found."))
        return product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product: Product = self.object
        gallery = list(product.gallery_images.all())
        context["gallery_images"] = gallery
        context["related_products"] = related_products(product, self.shop_language)
        context["breadcrumb_items"] = [
            home_crumb(),
            products_crumb(),
            (product.category.name, product.category.get_absolute_url()),
            (product.name, None),
        ]
        context["meta_title"] = product_meta_title(
            product, context.get("site_settings")
        )
        context["meta_description"] = (
            product.safe_translation_getter("meta_description")
            or product.safe_translation_getter("short_description", "")
        )
        context["canonical_url"] = self.request.build_absolute_uri()
        return context
