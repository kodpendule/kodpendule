"""JSON payloads for live cart updates."""

from __future__ import annotations

from django.utils.translation import ngettext

from apps.cart.cart import Cart
from apps.core.money import format_shop_money
from apps.core.utils import activate_parler_language, get_shop_language


def cart_state_json(request, cart: Cart) -> dict:
    lang = get_shop_language(request)
    lines = cart.get_lines()
    for line in lines:
        activate_parler_language(line.product, lang)

    item_count = cart.total_items
    return {
        "ok": True,
        "subtotal": str(cart.subtotal),
        "subtotal_display": format_shop_money(cart.subtotal),
        "item_count": item_count,
        "item_count_label": ngettext(
            "%(count)s item in your cart",
            "%(count)s items in your cart",
            item_count,
        )
        % {"count": item_count},
        "lines": [
            {
                "product_id": line.product.pk,
                "quantity": line.quantity,
                "line_total": str(line.line_total),
                "line_total_display": format_shop_money(line.line_total),
            }
            for line in lines
        ],
    }
