"""
Serbian admin phrasing for changelist titles, add buttons, and counts.

Uses full English msgids (translated in locale/sr) so labels follow Serbian
grammar (accusative, lowercase inside sentences) instead of Django's
``Select %(verbose_name)s`` + capitalized model names.
"""

from __future__ import annotations

from django.utils.translation import gettext_lazy as _

# app_label.model_name -> labels
CHANGELIST_TITLES: dict[str, str] = {
    "orders.order": _("Select order to change"),
    "products.product": _("Select product to change"),
    "categories.category": _("Select category to change"),
    "shipping.city": _("Select city to change"),
    "accounts.customercontact": _("Select customer contact to change"),
    "auth.group": _("Select group to change"),
    "auth.user": _("Select user to change"),
}

ADD_LABELS: dict[str, str] = {
    "orders.order": _("Add order"),
    "products.product": _("Add product"),
    "categories.category": _("Add category"),
    "shipping.city": _("Add city"),
    "accounts.customercontact": _("Add customer contact"),
    "auth.group": _("Add group"),
    "auth.user": _("Add user"),
}

# Singular / plural for pagination footer ("1 proizvod", "2 proizvoda")
COUNT_LABELS: dict[str, tuple[str, str]] = {
    "orders.order": (_("order"), _("orders")),
    "products.product": (_("product"), _("products")),
    "categories.category": (_("category"), _("categories")),
    "shipping.city": (_("city"), _("cities")),
    "accounts.customercontact": (_("customer contact"), _("customer contacts")),
    "auth.group": (_("group"), _("groups")),
    "auth.user": (_("user"), _("users")),
}


def model_ui_key(app_label: str, model_name: str) -> str:
    return f"{app_label}.{model_name}"


def changelist_ui_context(app_label: str, model_name: str) -> dict[str, str]:
    key = model_ui_key(app_label, model_name)
    ctx: dict[str, str] = {"kp_admin_breadcrumb_leaf": ""}
    if key in CHANGELIST_TITLES:
        ctx["kp_admin_changelist_title"] = CHANGELIST_TITLES[key]
    if key in ADD_LABELS:
        ctx["kp_admin_add_label"] = ADD_LABELS[key]
    if key in COUNT_LABELS:
        singular, plural = COUNT_LABELS[key]
        ctx["kp_admin_count_singular"] = singular
        ctx["kp_admin_count_plural"] = plural
    return ctx
