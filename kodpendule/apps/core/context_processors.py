from django.conf import settings

from apps.categories.selectors import get_nav_categories
from apps.core.models import FooterSettings, SiteSettings
from apps.core.utils import get_shop_language


def shop_globals(request):
    language = get_shop_language(request)
    site = SiteSettings.objects.language(language).filter(pk=1).first()
    footer = FooterSettings.objects.language(language).filter(pk=1).first()
    return {
        "site_settings": site,
        "footer_settings": footer,
        "nav_categories": get_nav_categories(language),
        "shop_currency_symbol": settings.SHOP_CURRENCY_SYMBOL,
        "shop_language": language,
    }
