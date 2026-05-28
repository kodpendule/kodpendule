"""Reusable HTML helpers for Django admin list and detail views."""

from __future__ import annotations

from decimal import Decimal

from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from apps.orders.models import OrderStatus
from apps.orders.status_display import STATUS_LABELS

_ORDER_STATUS_BADGE = {
    OrderStatus.PENDING: "neutral",
    OrderStatus.CONFIRMED: "info",
    OrderStatus.PROCESSING: "info",
    OrderStatus.SHIPPED: "warning",
    OrderStatus.DELIVERED: "success",
    OrderStatus.CANCELLED: "error",
}


def _status_variant(status: str) -> str:
    try:
        return _ORDER_STATUS_BADGE[OrderStatus(status)]
    except (KeyError, ValueError):
        return "neutral"


def admin_badge(label: str, variant: str = "neutral") -> str:
    return format_html(
        '<span class="kp-badge kp-badge--{}">{}</span>',
        variant,
        label,
    )


def order_status_badge(status: str) -> str:
    try:
        code = OrderStatus(status)
    except ValueError:
        code = status
    label = STATUS_LABELS.get(code, status)
    return admin_badge(str(label), _status_variant(status))


def money_cell(amount, *, emphasize: bool = False) -> str:
    text = f"{amount:,.2f}"
    if emphasize:
        return format_html('<span class="kp-money kp-money--emphasis">{}</span>', text)
    return format_html('<span class="kp-money">{}</span>', text)


def stock_cell(stock: int, *, is_low: bool, alert_at: int | None = None) -> str:
    if is_low:
        hint = _("low")
        if alert_at is not None:
            hint = _("low (alert ≤ %(n)s)") % {"n": alert_at}
        return format_html(
            '<span class="kp-stock kp-stock--low" title="{}">'
            '<span class="kp-stock__value">{}</span>'
            '<span class="kp-stock__flag">{}</span>'
            "</span>",
            hint,
            stock,
            _("Restock"),
        )
    return format_html('<span class="kp-stock">{}</span>', stock)


def slug_warning_cell(slug: str, missing_label: str | None = None) -> str:
    if slug:
        return format_html('<span class="kp-slug">{}</span>', slug)
    label = missing_label or _("missing — not on shop")
    return format_html(
        '<span class="kp-slug kp-slug--missing">{}</span>',
        label,
    )


def price_cell(
    effective: Decimal,
    *,
    base: Decimal | None = None,
    has_discount: bool = False,
) -> str:
    if has_discount and base is not None:
        return format_html(
            '<span class="kp-price">'
            '<span class="kp-price__was">{}</span> '
            '<span class="kp-price__now">{}</span>'
            "</span>",
            f"{base:,.2f}",
            f"{effective:,.2f}",
        )
    return format_html('<span class="kp-price__now">{}</span>', f"{effective:,.2f}")
