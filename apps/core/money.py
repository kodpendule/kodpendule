"""Shared storefront money formatting."""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings


def format_shop_money(value) -> str:
    if value is None:
        return ""
    if not isinstance(value, Decimal):
        value = Decimal(str(value))
    formatted = f"{value:,.2f}".replace(",", " ").replace(".", ",")
    return f"{formatted} {settings.SHOP_CURRENCY_SYMBOL}"
