from django.conf import settings
from django.http import Http404
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView

from apps.categories.selectors import (
    get_all_categories,
    get_category_by_slug,
    get_child_categories,
)
from apps.core.breadcrumbs import categories_crumb, home_crumb
from apps.core.mixins import ShopLanguageMixin
from apps.core.utils import activate_parler_language
from apps.core.templatetags.shop_tags import category_meta_title
from apps.products.selectors import filter_products_by_category


class CategoryListView(ShopLanguageMixin, ListView):
    template_name = "categories/list.html"
    context_object_name = "categories"

    def get_queryset(self):
        return get_all_categories(self.shop_language)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "breadcrumb_items": [home_crumb(), (_("Categories"), None)],
                "meta_title": _("Categories"),
                "meta_description": _("Browse product categories."),
                "canonical_url": self.request.build_absolute_uri(),
            }
        )
        return context


class CategoryDetailView(ShopLanguageMixin, ListView):
    template_name = "categories/detail.html"
    context_object_name = "products"
    paginate_by = settings.SHOP_PRODUCTS_PER_PAGE

    def dispatch(self, request, *args, **kwargs):
        self.category = get_category_by_slug(kwargs["slug"], self.shop_language)
        if self.category is None:
            raise Http404(_("Category not found."))
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return filter_products_by_category(
            self.category,
            self.shop_language,
            include_children=True,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for product in context.get("products", []):
            activate_parler_language(product, self.shop_language)
        category = self.category
        context.update(
            {
                "category": category,
                "active_category": category,
                "child_categories": get_child_categories(category, self.shop_language),
                "breadcrumb_items": [
                    home_crumb(),
                    categories_crumb(),
                    (category.name, None),
                ],
                "meta_title": category_meta_title(
                    category, context.get("site_settings")
                ),
                "meta_description": (
                    category.safe_translation_getter("meta_description")
                    or (category.safe_translation_getter("description") or "")[:160]
                ),
                "canonical_url": self.request.build_absolute_uri(),
            }
        )
        return context
