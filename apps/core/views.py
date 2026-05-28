from django.conf import settings
from django.db.models import F
from django.http import HttpRequest, HttpResponse
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from apps.core.contact_details import resolve_contact_details
from apps.core.mixins import ShopLanguageMixin
from apps.core.models import FooterSettings, SiteSettings
from apps.core.utils import activate_parler_language
from apps.categories.models import Category
from apps.categories.selectors import get_nav_categories
from apps.products.models import Product
from apps.products.selectors import active_products_qs, recommended_products_qs

RECOMMENDED_PRODUCTS_PER_PAGE = 5


class HomeView(ShopLanguageMixin, TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lang = self.shop_language
        site = SiteSettings.objects.language(lang).filter(pk=1).first()
        context.update(
            {
                "meta_title": (
                    site.safe_translation_getter("default_meta_title")
                    if site
                    else None
                )
                or (site.safe_translation_getter("site_name") if site else None),
                "meta_description": (
                    site.safe_translation_getter("default_meta_description") if site else ""
                ),
                "canonical_url": self.request.build_absolute_uri(),
            }
        )
        product_qs = active_products_qs(lang)

        new_arrivals = list(product_qs[:8])
        for product in new_arrivals:
            activate_parler_language(product, lang)

        promo_sale_products = list(
            product_qs.filter(
                discount_price__isnull=False,
                discount_price__lt=F("price"),
            )[:8]
        )
        for product in promo_sale_products:
            activate_parler_language(product, lang)

        featured_product = next(
            (p for p in new_arrivals if p.main_image),
            new_arrivals[0] if new_arrivals else None,
        )

        nav_categories = list(get_nav_categories(lang))
        for category in nav_categories:
            activate_parler_language(category, lang)

        recommended_products = list(recommended_products_qs(lang))
        for product in recommended_products:
            activate_parler_language(product, lang)

        recommended_product_pages = [
            recommended_products[i : i + RECOMMENDED_PRODUCTS_PER_PAGE]
            for i in range(0, len(recommended_products), RECOMMENDED_PRODUCTS_PER_PAGE)
        ]

        context.update(
            {
                "new_arrivals": new_arrivals,
                "promo_sale_products": promo_sale_products,
                "featured_product": featured_product,
                "home_nav_categories": nav_categories,
                "recommended_product_pages": recommended_product_pages,
                "recommended_products_total": len(recommended_products),
                "home_stats": {
                    "product_count": product_qs.count(),
                    "category_count": Category.objects.filter(is_active=True).count(),
                },
            }
        )
        return context


class ContactView(ShopLanguageMixin, TemplateView):
    template_name = "pages/contact.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lang = self.shop_language
        footer = FooterSettings.objects.language(lang).filter(pk=1).first()
        context.update(
            {
                "meta_title": _("Contact"),
                "canonical_url": self.request.build_absolute_uri(),
                "contact_details": resolve_contact_details(footer),
            }
        )
        return context


def robots_txt(request: HttpRequest) -> HttpResponse:
    """Crawler rules for the storefront; sitemap URL follows the current host."""
    sitemap_url = request.build_absolute_uri("/sitemap.xml")
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /korpa/",
        "Disallow: /placanje/",
        "Disallow: /prijava/",
        "Disallow: /registracija/",
        "Disallow: /odjava/",
        "Disallow: /nalog/",
        "Disallow: /narudzba/",
        "Disallow: /jezik/",
        "",
        f"Sitemap: {sitemap_url}",
    ]
    if settings.DEBUG:
        lines.insert(2, "Disallow: /")
    body = "\n".join(lines) + "\n"
    return HttpResponse(body, content_type="text/plain; charset=utf-8")
