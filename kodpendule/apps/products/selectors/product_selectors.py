from django.db.models import Q, QuerySet

from apps.categories.models import Category
from apps.core.models import HomepageSectionType
from apps.core.utils import get_shop_language
from apps.products.models import Product


def _language(language: str | None) -> str:
    return language or get_shop_language()


def active_products_qs(language: str | None = None) -> QuerySet[Product]:
    """Base queryset for storefront product lists."""
    lang = _language(language)
    return (
        Product.objects.filter(is_active=True)
        .select_related("category")
        .prefetch_related("translations", "category__translations", "gallery_images")
        .order_by("-created_at")
    )


def get_product_by_slug(slug: str, language: str | None = None) -> Product | None:
    lang = _language(language)
    product = (
        Product.objects.filter(
            is_active=True,
            translations__language_code=lang,
            translations__slug=slug,
        )
        .select_related("category")
        .prefetch_related("translations", "category__translations", "gallery_images")
        .distinct()
        .first()
    )
    if product is not None:
        product.set_current_language(lang)
    return product


def filter_products_by_category(
    category: Category,
    language: str | None = None,
    *,
    include_children: bool = False,
) -> QuerySet[Product]:
    qs = active_products_qs(language)
    if include_children:
        category_ids = _collect_category_ids(category, language)
        return qs.filter(category_id__in=category_ids)
    return qs.filter(category=category)


def _collect_category_ids(category: Category, language: str | None) -> list[int]:
    ids = [category.pk]
    children = (
        Category.objects.filter(is_active=True, parent=category)
        .values_list("pk", flat=True)
    )
    for child_id in children:
        child = Category.objects.filter(pk=child_id).first()
        if child:
            ids.extend(_collect_category_ids(child, language))
    return ids


def search_products(query: str, language: str | None = None) -> QuerySet[Product]:
    q = query.strip()
    if not q:
        return active_products_qs(language).none()
    lang = _language(language)
    return active_products_qs(lang).filter(
        Q(sku__icontains=q)
        | Q(translations__language_code=lang, translations__name__icontains=q)
        | Q(
            translations__language_code=lang,
            translations__short_description__icontains=q,
        )
    ).distinct()


def products_for_homepage_section(
    section_type: str,
    limit: int,
    language: str | None = None,
) -> QuerySet[Product]:
    qs = active_products_qs(language)
    if section_type == HomepageSectionType.FEATURED:
        qs = qs.filter(is_featured=True)
    elif section_type == HomepageSectionType.RECOMMENDED:
        qs = qs.filter(is_recommended=True)
    elif section_type == HomepageSectionType.SALE:
        qs = qs.filter(is_on_sale=True)
    else:
        return qs.none()
    return qs[:limit]


def related_products(product: Product, language: str | None = None, limit: int = 4) -> QuerySet[Product]:
    return (
        active_products_qs(language)
        .filter(category=product.category)
        .exclude(pk=product.pk)[:limit]
    )
