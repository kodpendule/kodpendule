from django.conf import settings
from django.views.generic import TemplateView

from apps.core.mixins import ShopLanguageMixin
from apps.core.models import SiteSettings
from apps.core.selectors import (
    get_active_hero_banners,
    get_homepage_bottom_promos,
    get_homepage_middle_promos,
    get_homepage_product_blocks,
)


class HomeView(ShopLanguageMixin, TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lang = self.shop_language
        site = SiteSettings.objects.language(lang).filter(pk=1).first()
        context.update(
            {
                "hero_banners": get_active_hero_banners(lang),
                "homepage_blocks": get_homepage_product_blocks(lang),
                "promo_middle": get_homepage_middle_promos(lang),
                "promo_bottom": get_homepage_bottom_promos(lang),
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
        return context


class ContactView(ShopLanguageMixin, TemplateView):
    template_name = "pages/contact.html"

    def get_context_data(self, **kwargs):
        from django.utils.translation import gettext_lazy as _

        context = super().get_context_data(**kwargs)
        context["meta_title"] = _("Contact")
        context["canonical_url"] = self.request.build_absolute_uri()
        return context
