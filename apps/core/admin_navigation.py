"""
Grouped admin navigation (Phase 2).

Maps Django admin app_list entries into store-manager sections without
changing ModelAdmin registration.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from django.http import HttpRequest
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


@dataclass
class AdminNavItem:
    name: str
    url: str
    active: bool = False
    add_url: str | None = None
    description: str = ""


@dataclass
class AdminNavSection:
    id: str
    title: str
    items: list[AdminNavItem] = field(default_factory=list)


# Model keys: "{app_label}.{model_object_name_lower}"
_NAV_SECTION_SPECS: list[tuple[str, str, list[str]]] = [
    ("orders", _("Orders"), ["orders.order"]),
    ("products", _("Products"), ["products.product"]),
    ("categories", _("Categories"), ["categories.category"]),
    ("shipping", _("Shipping"), ["shipping.city", "shipping.shippingmethod"]),
    ("customers", _("Customers"), ["accounts.customercontact"]),
    ("analytics", _("Analytics"), []),
]

_HIDDEN_MODEL_KEYS: set[str] = {
    "accounts.user",
    "accounts.address",
    "core.sitesettings",
    "core.footersettings",
}


def _model_lookup(available_apps: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    lookup: dict[str, dict[str, Any]] = {}
    for app in available_apps:
        app_label = app["app_label"]
        for model in app["models"]:
            key = f"{app_label}.{model['object_name'].lower()}"
            lookup[key] = model
    return lookup


def _is_promo_sales_page(request: HttpRequest) -> bool:
    promo_path = reverse("admin:products_product_promo_sales")
    return request.path == promo_path or request.path.startswith(promo_path.rstrip("/") + "/")


def _is_recommended_products_page(request: HttpRequest) -> bool:
    path = reverse("admin:products_product_recommended")
    return request.path == path or request.path.startswith(path.rstrip("/") + "/")


def _is_active(url: str, request: HttpRequest) -> bool:
    if not url:
        return False
    path = request.path
    if path == url:
        return True
    if not path.startswith(url.rstrip("/") + "/"):
        return False
    # Custom product tools live under /products/product/ — do not highlight the changelist too.
    if _is_promo_sales_page(request) or _is_recommended_products_page(request):
        changelist = reverse("admin:products_product_changelist")
        if url.rstrip("/") == changelist.rstrip("/"):
            return False
    # Low-stock anchor should not mark the main analytics link active.
    dashboard_url = reverse("dashboard:index")
    if (
        url.rstrip("/") == dashboard_url.rstrip("/")
        and request.get_full_path() != url
        and "#" in request.get_full_path()
    ):
        return False
    return True


def _promo_sales_item(request: HttpRequest) -> AdminNavItem:
    url = reverse("admin:products_product_promo_sales")
    return AdminNavItem(
        name=_("Promo sales"),
        url=url,
        active=_is_active(url, request),
        description=_("Apply discounts to multiple products"),
    )


def _recommended_products_item(request: HttpRequest) -> AdminNavItem:
    url = reverse("admin:products_product_recommended")
    return AdminNavItem(
        name=_("Recommended products"),
        url=url,
        active=_is_active(url, request),
        description=_("Choose products for the homepage carousel"),
    )


def _analytics_items(request: HttpRequest) -> list[AdminNavItem]:
    dashboard_url = reverse("dashboard:index")
    items = [
        AdminNavItem(
            name=_("Shop analytics"),
            url=dashboard_url,
            active=_is_active(dashboard_url, request)
            and "#" not in request.get_full_path(),
            description=_("Sales overview, charts, and reports"),
        ),
        AdminNavItem(
            name=_("Low stock alerts"),
            url=f"{dashboard_url}#kp-low-stock-alerts",
            active="kp-low-stock-alerts" in request.get_full_path()
            or request.GET.get("section") == "low-stock",
            description=_("Products that need restocking"),
        ),
    ]
    return items


def get_admin_nav_sections(
    available_apps: list[dict[str, Any]],
    request: HttpRequest,
) -> list[AdminNavSection]:
    """Build grouped navigation for sidebar and admin home."""
    lookup = _model_lookup(available_apps)
    used_keys: set[str] = set()
    sections: list[AdminNavSection] = []

    for section_id, title, model_keys in _NAV_SECTION_SPECS:
        items: list[AdminNavItem] = []

        if section_id == "analytics":
            items.extend(_analytics_items(request))
        else:
            for key in model_keys:
                model = lookup.get(key)
                if not model or not model.get("admin_url"):
                    continue
                used_keys.add(key)
                items.append(
                    AdminNavItem(
                        name=model["name"],
                        url=model["admin_url"],
                        active=_is_active(model["admin_url"], request),
                        add_url=model.get("add_url"),
                    )
                )
            if section_id == "products" and request.user.has_perm("products.change_product"):
                items.append(_promo_sales_item(request))
                items.append(_recommended_products_item(request))

        if items:
            sections.append(AdminNavSection(id=section_id, title=title, items=items))

    remaining: list[AdminNavItem] = []
    for key, model in sorted(lookup.items()):
        if key in used_keys or key in _HIDDEN_MODEL_KEYS or not model.get("admin_url"):
            continue
        remaining.append(
            AdminNavItem(
                name=model["name"],
                url=model["admin_url"],
                active=_is_active(model["admin_url"], request),
                add_url=model.get("add_url"),
            )
        )

    if remaining:
        sections.append(
            AdminNavSection(id="other", title=_("Other"), items=remaining),
        )

    return sections
