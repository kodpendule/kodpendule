"""Email staff when a new order is placed."""

from __future__ import annotations

import logging

from django.conf import settings
from django.core.mail import send_mail
from django.utils.translation import gettext as _

from apps.core.contact_details import resolve_contact_details
from apps.core.models import FooterSettings
from apps.orders.models import Order

logger = logging.getLogger(__name__)


def order_notification_recipients() -> list[str]:
    configured = getattr(settings, "SHOP_ORDER_NOTIFICATION_EMAILS", None) or []
    if configured:
        return [email.strip() for email in configured if email and email.strip()]

    footer = FooterSettings.objects.filter(pk=1).first()
    contact = resolve_contact_details(footer)
    if contact.email:
        return [contact.email.strip()]
    return []


def notify_staff_new_order(order: Order) -> None:
    """Notify shop staff about a new order. Failures are logged, not raised."""
    recipients = order_notification_recipients()
    if not recipients:
        logger.warning(
            "No order notification recipients configured; skipped email for %s",
            order.order_number,
        )
        return

    subject = _("New order %(number)s") % {"number": order.order_number}
    lines = [
        _("A new order was placed on the shop."),
        "",
        _("Order number: %(number)s") % {"number": order.order_number},
        _("Customer: %(name)s") % {"name": order.customer_full_name},
        _("Email: %(email)s") % {"email": order.customer_email},
        _("Phone: %(phone)s") % {"phone": order.phone},
        _("Total: %(total)s") % {"total": order.total},
        _("Delivery city: %(city)s") % {"city": order.shipping_city_name},
        _("Delivery street: %(street)s") % {"street": order.shipping_street},
    ]
    if order.delivery_date:
        lines.append(
            _("Preferred delivery date: %(date)s") % {"date": order.delivery_date.isoformat()}
        )
    if order.order_notes:
        lines.append("")
        lines.append(_("Order notes:"))
        lines.append(order.order_notes)

    try:
        send_mail(
            subject=subject,
            message="\n".join(lines),
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None) or recipients[0],
            recipient_list=recipients,
            fail_silently=False,
        )
    except Exception:
        logger.exception(
            "Failed to send order notification email for %s",
            order.order_number,
        )
