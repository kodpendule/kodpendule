from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.checkout_settings import ThresholdShippingMode
from apps.core.fields import MoneyField


class City(models.Model):
    """Delivery location with flat shipping price (RSD)."""

    name = models.CharField(_("Name"), max_length=120, unique=True)
    slug = models.SlugField(_("Slug"), max_length=140, unique=True)
    shipping_price = MoneyField(verbose_name=_("Shipping price (RSD)"), default=0)
    promo_cart_threshold = MoneyField(
        verbose_name=_("Cart total threshold"),
        null=True,
        blank=True,
        help_text=_(
            "When the cart subtotal is at or above this amount (RSD), "
            "the promotional delivery rule below applies. Leave empty to disable."
        ),
    )
    promo_shipping_mode = models.CharField(
        verbose_name=_("When threshold is reached"),
        max_length=20,
        choices=ThresholdShippingMode.choices,
        default=ThresholdShippingMode.FREE,
        help_text=_(
            "Choose free delivery or the discounted shipping price configured below."
        ),
    )
    promo_discounted_shipping_price = MoneyField(
        verbose_name=_("Discounted shipping price"),
        null=True,
        blank=True,
        help_text=_(
            "Used when threshold is reached and mode is “Discounted shipping price”. "
            "Leave empty if you only use free shipping."
        ),
    )
    is_active = models.BooleanField(_("Active"), default=True)
    sort_order = models.PositiveIntegerField(_("Sort order"), default=0)

    class Meta:
        verbose_name = _("city")
        verbose_name_plural = _("cities")
        ordering = ["sort_order", "name"]
        indexes = [
            models.Index(fields=["is_active", "sort_order"]),
        ]

    def __str__(self) -> str:
        return self.name
