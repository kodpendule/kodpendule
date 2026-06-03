"""JSON payloads for live cart updates."""

from __future__ import annotations

from django.utils.translation import gettext_lazy as _, ngettext

from apps.cart.cart import Cart
from apps.core.money import format_shop_money
from apps.core.storefront_urls import shop_reverse
from apps.core.utils import activate_parler_language, get_shop_language
from apps.products.models import Product


def _cart_line_json(request, line) -> dict:
    product = line.product
    image_url = ""
    if product.main_image:
        image_url = product.main_image.url
    lang = get_shop_language(request)
    return {
        "product_id": product.pk,
        "name": product.safe_translation_getter("name", any_language=True),
        "url": product.get_absolute_url(),
        "image_url": image_url,
        "quantity": line.quantity,
        "stock": product.stock,
        "unit_price_display": format_shop_money(line.unit_price),
        "line_total": str(line.line_total),
        "line_total_display": format_shop_money(line.line_total),
        "update_url": shop_reverse(
            "cart:update",
            product_id=product.pk,
            language=lang,
        ),
        "remove_url": shop_reverse(
            "cart:remove",
            product_id=product.pk,
            language=lang,
        ),
    }


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
        "lines": [_cart_line_json(request, line) for line in lines],
    }


def cart_add_json(request, cart: Cart, product: Product) -> dict:
    lang = get_shop_language(request)
    product.set_current_language(lang)
    name = product.safe_translation_getter("name", any_language=True)
    payload = cart_state_json(request, cart)
    payload["message"] = _("“%(name)s” added to cart.") % {"name": name}
    payload["product_id"] = product.pk
    return payload
