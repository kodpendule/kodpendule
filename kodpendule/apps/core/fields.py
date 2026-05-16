"""Reusable model field definitions."""

from django.db import models

MONEY_MAX_DIGITS = 12
MONEY_DECIMAL_PLACES = 2


def MoneyField(**kwargs: object) -> models.DecimalField:
    """Decimal field for RSD amounts."""
    defaults = {
        "max_digits": MONEY_MAX_DIGITS,
        "decimal_places": MONEY_DECIMAL_PLACES,
    }
    defaults.update(kwargs)
    return models.DecimalField(**defaults)
