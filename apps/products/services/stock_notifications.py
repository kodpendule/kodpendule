"""Low-stock email alerts for shop administrators."""

from __future__ import annotations

import logging

from django.utils.translation import gettext as _

from apps.core.email_recipients import shop_admin_recipients
from apps.core.mail import send_shop_email
from apps.products.models import Product

logger = logging.getLogger(__name__)


def notify_low_stock_if_crossed_threshold(
    *,
    product: Product,
    stock_before: int,
) -> None:
    """
    Email admins when stock drops from above the alert threshold to at/below it.
    """
    threshold = product.minimum_stock_alert
    stock_after = product.stock

    if stock_before > threshold >= stock_after:
        notify_low_stock(product)


def notify_low_stock(product: Product) -> None:
    recipients = shop_admin_recipients()
    if not recipients:
        logger.warning(
            "Low stock email skipped: no recipients (product %s)",
            product.sku,
        )
        return

    name = product.safe_translation_getter("name", any_language=True) or product.sku
    subject = _("Low stock: %(name)s") % {"name": name}
    body = "\n".join(
        [
            _("A product has reached the low-stock alert threshold."),
            "",
            _("Product: %(name)s") % {"name": name},
            _("SKU: %(sku)s") % {"sku": product.sku},
            _("Stock remaining: %(stock)s") % {"stock": product.stock},
            _("Alert threshold: %(threshold)s") % {"threshold": product.minimum_stock_alert},
        ]
    )

    send_shop_email(
        subject=subject,
        message=body,
        recipient_list=recipients,
    )
