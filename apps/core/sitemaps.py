"""Sitemap sections for public storefront URLs."""

from __future__ import annotations

from django.conf import settings
from django.contrib.sitemaps import Sitemap

from apps.categories.models import Category
from apps.categories.selectors.category_selectors import active_categories_qs
from apps.core.slugs import localized_slug
from apps.core.storefront_urls import shop_reverse
from apps.products.models import Product
from apps.products.selectors.product_selectors import active_products_qs

_DEFAULT_LANG = settings.PARLER_DEFAULT_LANGUAGE_CODE


class StaticViewSitemap(Sitemap):
    """Home, contact, and catalog index pages."""

    priority = 0.8
    changefreq = "weekly"

    def items(self) -> list[str]:
        return [
            "core:home",
            "core:contact",
            "core:terms",
            "core:privacy",
            "products:list",
            "categories:list",
        ]

    def location(self, item: str) -> str:
        return shop_reverse(item, language=_DEFAULT_LANG)


class CategorySitemap(Sitemap):
    priority = 0.7
    changefreq = "weekly"

    def items(self) -> list[Category]:
        categories = active_categories_qs(language=_DEFAULT_LANG)
        return [
            category
            for category in categories
            if localized_slug(category, language=_DEFAULT_LANG)
        ]

    def lastmod(self, obj: Category):
        return obj.updated_at

    def location(self, obj: Category) -> str:
        slug = localized_slug(obj, language=_DEFAULT_LANG)
        return shop_reverse("categories:detail", language=_DEFAULT_LANG, slug=slug)


class ProductSitemap(Sitemap):
    priority = 0.6
    changefreq = "weekly"

    def items(self) -> list[Product]:
        return list(active_products_qs(language=_DEFAULT_LANG))

    def lastmod(self, obj: Product):
        return obj.updated_at

    def location(self, obj: Product) -> str:
        slug = localized_slug(obj, language=_DEFAULT_LANG)
        if not slug:
            return shop_reverse("products:list", language=_DEFAULT_LANG)
        return shop_reverse("products:detail", language=_DEFAULT_LANG, slug=slug)


sitemaps = {
    "static": StaticViewSitemap,
    "categories": CategorySitemap,
    "products": ProductSitemap,
}
