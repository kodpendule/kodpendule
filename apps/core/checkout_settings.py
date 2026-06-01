"""Checkout delivery promotion helpers."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class ThresholdShippingMode(models.TextChoices):
    FREE = "free", _("Free shipping")
    DISCOUNTED = "discounted", _("Discounted shipping price")


class DeliveryTiming(models.TextChoices):
    SAME_DAY = "same_day", _("Deliver today (as soon as possible)")
    SCHEDULED = "scheduled", _("Schedule for a later date")


def checkout_today() -> date:
    return timezone.localdate()


def min_scheduled_delivery_date(*, from_date: date | None = None) -> date:
    """Earliest selectable date for free scheduled delivery (day after order day)."""
    base = from_date or checkout_today()
    return base + timedelta(days=1)


def resolve_checkout_shipping_price(
    *,
    subtotal: Decimal,
    city,
    requested_delivery_date: date | None = None,
    order_date: date | None = None,
) -> Decimal:
    """
    Future scheduled delivery is free.
    Same-day delivery uses the city's base price and cart-threshold promos.
    """
    today = order_date or checkout_today()
    delivery_date = requested_delivery_date or today
    if delivery_date > today:
        return Decimal("0")

    threshold = city.promo_cart_threshold
    base_price = city.shipping_price

    if threshold is None or threshold <= 0 or subtotal < threshold:
        return base_price

    if city.promo_shipping_mode == ThresholdShippingMode.FREE:
        return Decimal("0")

    if city.promo_discounted_shipping_price is not None:
        return city.promo_discounted_shipping_price

    return base_price
