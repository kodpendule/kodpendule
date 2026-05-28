from django.conf import settings

from apps.cart.cart import get_cart
from apps.categories.selectors import get_nav_categories
from apps.core.contact_details import resolve_contact_details
from apps.core.models import FooterSettings, SiteSettings
from apps.core.utils import get_shop_language


def shop_globals(request):
    language = get_shop_language(request)
    site = SiteSettings.objects.language(language).filter(pk=1).first()
    footer = FooterSettings.objects.language(language).filter(pk=1).first()
    cart = get_cart(request)
    return {
        "site_settings": site,
        "footer_settings": footer,
        "footer_contact": resolve_contact_details(footer),
        "nav_categories": get_nav_categories(language),
        "shop_currency_symbol": settings.SHOP_CURRENCY_SYMBOL,
        "shop_language": language,
        "cart_item_count": cart.total_items,
    }
