"""Singleton checkout / shipping promotion settings (pk=1)."""

from __future__ import annotations

from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.fields import MoneyField


class ThresholdShippingMode(models.TextChoices):
    FREE = "free", _("Free shipping")
    DISCOUNTED = "discounted", _("Discounted shipping price")


class CheckoutSettings(models.Model):
    """
    Store-wide checkout rules editable in admin (no code deploy needed).
    """

    free_shipping_threshold = MoneyField(
        verbose_name=_("Free shipping threshold"),
        null=True,
        blank=True,
        help_text=_(
            "When the cart subtotal is at or above this amount (RSD), "
            "the threshold shipping rule below applies. Leave empty to disable."
        ),
    )
    threshold_shipping_mode = models.CharField(
        verbose_name=_("When threshold is reached"),
        max_length=20,
        choices=ThresholdShippingMode.choices,
        default=ThresholdShippingMode.FREE,
        help_text=_(
            "Choose free delivery or the discounted shipping price configured below."
        ),
    )
    discounted_shipping_price = MoneyField(
        verbose_name=_("Discounted shipping price"),
        null=True,
        blank=True,
        help_text=_(
            "Used when threshold is reached and mode is “Discounted shipping price”. "
            "Leave empty if you only use free shipping."
        ),
    )

    class Meta:
        verbose_name = _("checkout settings")
        verbose_name_plural = _("checkout settings")

    def save(self, *args, **kwargs) -> None:
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) -> None:
        pass

    @classmethod
    def load(cls) -> "CheckoutSettings":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


def resolve_checkout_shipping_price(*, subtotal: Decimal, city_shipping_price: Decimal) -> Decimal:
    """Apply admin threshold rules to the city's base delivery price."""
    settings = CheckoutSettings.load()
    threshold = settings.free_shipping_threshold

    if threshold is None or threshold <= 0 or subtotal < threshold:
        return city_shipping_price

    if settings.threshold_shipping_mode == ThresholdShippingMode.FREE:
        return Decimal("0")

    if settings.discounted_shipping_price is not None:
        return settings.discounted_shipping_price

    return city_shipping_price
