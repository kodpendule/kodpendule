"""
Serbian URL segments for Django admin (canonical paths under /admin/).

Storefront URLs stay in apps/*/urls.py (proizvodi/, kategorije/, …).
English admin paths (products/product/) redirect here for bookmarks.
"""

from __future__ import annotations

from django.db.models import Model

# "{app_label}.{model_name}" -> single path segment
MODEL_ADMIN_SLUGS: dict[str, str] = {
    "orders.order": "narudzbine",
    "products.product": "proizvodi",
    "categories.category": "kategorije",
    "shipping.city": "gradovi",
    "accounts.customercontact": "kontakti-kupaca",
    "accounts.user": "korisnici",
}

# Legacy English segments (app/model) -> Serbian slug
LEGACY_ADMIN_PATHS: dict[str, str] = {
    "orders/order": "narudzbine",
    "products/product": "proizvodi",
    "categories/category": "kategorije",
    "shipping/city": "gradovi",
    "accounts/customercontact": "kontakti-kupaca",
    "accounts/user": "korisnici",
}

DASHBOARD_ADMIN_SLUG = "analitika"


def model_admin_slug(model: type[Model]) -> str | None:
    key = f"{model._meta.app_label}.{model._meta.model_name}"
    return MODEL_ADMIN_SLUGS.get(key)


def admin_path_for_model(model: type[Model]) -> str:
    slug = model_admin_slug(model)
    if slug:
        return f"{slug}/"
    return f"{model._meta.app_label}/{model._meta.model_name}/"
