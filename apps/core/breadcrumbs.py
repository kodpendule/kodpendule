from django.utils.translation import gettext_lazy as _

from apps.core.storefront_urls import shop_reverse


def home_crumb():
    return (_("Home"), shop_reverse("core:home"))


def categories_crumb():
    return (_("Categories"), shop_reverse("categories:list"))


def products_crumb():
    return (_("Products"), shop_reverse("products:list"))


def category_breadcrumb_items(category, language: str, *, link_current_category: bool = False):
    """
    Home → Categories → …ancestors → category.
    Category detail pages omit the link on the current category; product pages link it.
    """
    from apps.categories.models import Category
    from apps.core.utils import activate_parler_language

    items = [home_crumb(), categories_crumb()]
    ancestors = []
    current = category.parent
    while current is not None:
        if current.is_active:
            activate_parler_language(current, language)
            ancestors.append((current.name, current.get_absolute_url()))
        parent_id = current.parent_id
        current = (
            Category.objects.filter(pk=parent_id, is_active=True)
            .select_related("parent")
            .prefetch_related("translations")
            .first()
            if parent_id
            else None
        )
    ancestors.reverse()
    items.extend(ancestors)
    activate_parler_language(category, language)
    if link_current_category:
        items.append((category.name, category.get_absolute_url()))
    else:
        items.append((category.name, None))
    return items
