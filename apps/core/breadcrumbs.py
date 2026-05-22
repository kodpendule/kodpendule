from django.urls import reverse
from django.utils.translation import gettext_lazy as _


def home_crumb():
    return (_("Home"), reverse("core:home"))


def categories_crumb():
    return (_("Categories"), reverse("categories:list"))


def products_crumb():
    return (_("Products"), reverse("products:list"))
