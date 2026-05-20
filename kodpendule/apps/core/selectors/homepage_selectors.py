from dataclasses import dataclass, field

from django.db.models import QuerySet

from apps.core.models import HeroBanner, HomepageSection, PromoPlacement, PromoSection
from apps.core.utils import get_shop_language
from apps.products.models import Product
from apps.products.selectors.product_selectors import products_for_homepage_section


@dataclass
class HomepageProductBlock:
    section: HomepageSection
    products: QuerySet[Product] = field(default_factory=Product.objects.none)


def get_active_hero_banners(language: str | None = None) -> QuerySet[HeroBanner]:
    lang = language or get_shop_language()
    return (
        HeroBanner.objects.filter(is_active=True)
        .language(lang)
        .prefetch_related("translations")
        .order_by("sort_order", "id")
    )


def get_promo_sections(
    placement: str,
    language: str | None = None,
) -> QuerySet[PromoSection]:
    lang = language or get_shop_language()
    return (
        PromoSection.objects.filter(is_active=True, placement=placement)
        .language(lang)
        .prefetch_related("translations")
        .order_by("sort_order", "id")
    )


def get_homepage_product_blocks(language: str | None = None) -> list[HomepageProductBlock]:
    lang = language or get_shop_language()
    blocks: list[HomepageProductBlock] = []
    for section in HomepageSection.objects.filter(is_active=True).order_by("section_type"):
        products = products_for_homepage_section(
            section.section_type,
            section.max_products,
            lang,
        )
        if products.exists():
            blocks.append(HomepageProductBlock(section=section, products=products))
    return blocks


def get_homepage_middle_promos(language: str | None = None) -> QuerySet[PromoSection]:
    return get_promo_sections(PromoPlacement.HOMEPAGE_MIDDLE, language)


def get_homepage_bottom_promos(language: str | None = None) -> QuerySet[PromoSection]:
    return get_promo_sections(PromoPlacement.HOMEPAGE_BOTTOM, language)
