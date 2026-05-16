from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.fields import MoneyField


class City(models.Model):
    """Delivery location with flat shipping price (RSD)."""

    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    shipping_price = MoneyField(default=0)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _("city")
        verbose_name_plural = _("cities")
        ordering = ["sort_order", "name"]
        indexes = [
            models.Index(fields=["is_active", "sort_order"]),
        ]

    def __str__(self) -> str:
        return self.name


class ShippingMethod(models.Model):
    """Reserved for future carrier / pickup options."""

    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("shipping method")
        verbose_name_plural = _("shipping methods")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name
