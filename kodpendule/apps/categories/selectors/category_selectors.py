from django.db.models import Prefetch, QuerySet

from apps.categories.models import Category
from apps.core.utils import get_shop_language


def _language(language: str | None) -> str:
    return language or get_shop_language()


def active_categories_qs(language: str | None = None) -> QuerySet[Category]:
    lang = _language(language)
    return (
        Category.objects.filter(is_active=True)
        .prefetch_related("translations")
        .order_by("sort_order", "pk")
    )


def get_nav_categories(language: str | None = None) -> QuerySet[Category]:
    """Top-level categories for header navigation."""
    return active_categories_qs(language).filter(parent__isnull=True)


def get_category_by_slug(slug: str, language: str | None = None) -> Category | None:
    lang = _language(language)
    category = (
        Category.objects.filter(
            is_active=True,
            translations__language_code=lang,
            translations__slug=slug,
        )
        .select_related("parent")
        .prefetch_related("translations")
        .distinct()
        .first()
    )
    if category is not None:
        category.set_current_language(lang)
    return category


def get_child_categories(parent: Category, language: str | None = None) -> QuerySet[Category]:
    lang = _language(language)
    return (
        active_categories_qs(lang)
        .filter(parent=parent)
        .prefetch_related(
            Prefetch(
                "children",
                queryset=active_categories_qs(lang),
            )
        )
    )


def get_all_categories(language: str | None = None) -> QuerySet[Category]:
    """Flat list for category index page."""
    return active_categories_qs(language).select_related("parent")
