"""Plain-text bodies for order-related emails."""

from __future__ import annotations

from django.utils.translation import gettext as _

from apps.core.locale_dates import latin_short_date
from apps.core.money import format_shop_money
from apps.orders.models import Order


def build_order_details_text(order: Order) -> str:
    order = (
        Order.objects.filter(pk=order.pk)
        .prefetch_related("items")
        .select_related("shipping_city")
        .first()
        or order
    )

    lines = [
        _("Order number: %(number)s") % {"number": order.order_number},
        "",
        _("Customer"),
        _("Name: %(name)s") % {"name": order.customer_full_name},
        _("Email: %(email)s") % {"email": order.customer_email},
        _("Phone: %(phone)s") % {"phone": order.phone},
        "",
        _("Delivery"),
        _("Address: %(street)s") % {"street": order.shipping_street},
        _("City: %(city)s") % {"city": order.shipping_city_name},
        _("Requested delivery date: %(date)s")
        % {"date": latin_short_date(order.requested_delivery_date)},
    ]
    if order.order_notes:
        lines.extend(["", _("Notes: %(notes)s") % {"notes": order.order_notes}])

    lines.extend(
        [
            "",
            _("Payment method: %(method)s")
            % {"method": order.get_payment_method_display()},
        ]
    )

    lines.extend(["", _("Products")])
    for item in order.items.all():
        line_total = item.unit_price * item.quantity
        lines.append(
            _("- %(name)s × %(qty)s @ %(unit)s = %(total)s")
            % {
                "name": item.product_name,
                "qty": item.quantity,
                "unit": format_shop_money(item.unit_price),
                "total": format_shop_money(line_total),
            }
        )

    lines.extend(
        [
            "",
            _("Subtotal: %(amount)s") % {"amount": format_shop_money(order.subtotal)},
            _("Shipping: %(amount)s") % {"amount": format_shop_money(order.shipping_price)},
            _("Total: %(amount)s") % {"amount": format_shop_money(order.total)},
        ]
    )
    return "\n".join(lines)
