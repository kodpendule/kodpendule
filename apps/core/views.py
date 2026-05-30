from django.conf import settings
from django.db.models import F
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.utils.translation import check_for_language, gettext_lazy as _
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView

from apps.core.contact_details import resolve_contact_details
from apps.core.mixins import ShopLanguageMixin
from apps.core.models import FooterSettings, SiteSettings
from apps.core.utils import activate_parler_language
from apps.categories.models import Category
from apps.categories.selectors import get_nav_categories
from apps.products.models import Product
from apps.products.selectors import active_products_qs, recommended_products_qs


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

        recommended_products = list(recommended_products_qs(lang))
        for product in recommended_products:
            activate_parler_language(product, lang)

        nav_categories = list(get_nav_categories(lang))
        for category in nav_categories:
            activate_parler_language(category, lang)

        # Editorial spotlight only — admin-picked recommended product with an image.
        featured_product = next(
            (p for p in recommended_products if p.main_image),
            None,
        )

        context.update(
            {
                "new_arrivals": new_arrivals,
                "promo_sale_products": promo_sale_products,
                "featured_product": featured_product,
                "home_nav_categories": nav_categories,
                "recommended_products": recommended_products,
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
    from apps.core.storefront_urls import storefront_paths_for_robots

    sitemap_url = request.build_absolute_uri("/sitemap.xml")
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
    ]
    for path_prefix in storefront_paths_for_robots():
        if path_prefix not in ("/",):
            lines.append(f"Disallow: {path_prefix}")
    lines.extend(
        [
            "",
            f"Sitemap: {sitemap_url}",
        ]
    )
    if settings.DEBUG:
        lines.insert(2, "Disallow: /")
    body = "\n".join(lines) + "\n"
    return HttpResponse(body, content_type="text/plain; charset=utf-8")


@require_POST
def set_shop_language(request: HttpRequest) -> HttpResponse:
    """Set storefront language cookie and redirect to the localized equivalent URL."""
    from django.utils import translation
    from urllib.parse import urlsplit, urlunsplit

    from apps.core.storefront_urls import translate_storefront_url

    language = request.POST.get("language")
    next_url = request.POST.get("next") or "/"
    if not language or not check_for_language(language):
        return HttpResponseRedirect(next_url)

    parts = urlsplit(next_url)
    localized_path = translate_storefront_url(parts.path, language)
    redirect_to = urlunsplit(
        (parts.scheme, parts.netloc, localized_path, parts.query, parts.fragment)
    )

    translation.activate(language)
    response = HttpResponseRedirect(redirect_to)
    response.set_cookie(
        settings.LANGUAGE_COOKIE_NAME,
        language,
        max_age=settings.LANGUAGE_COOKIE_AGE,
        path=settings.LANGUAGE_COOKIE_PATH,
        domain=settings.LANGUAGE_COOKIE_DOMAIN,
        secure=settings.LANGUAGE_COOKIE_SECURE,
        httponly=settings.LANGUAGE_COOKIE_HTTPONLY,
        samesite=settings.LANGUAGE_COOKIE_SAMESITE,
    )
    return response
