from django.utils.translation import gettext_lazy as _

from apps.core.storefront_urls import shop_reverse


def home_crumb():
    return (_("Home"), shop_reverse("core:home"))


def categories_crumb():
    return (_("Categories"), shop_reverse("categories:list"))


def products_crumb():
    return (_("Products"), shop_reverse("products:list"))
