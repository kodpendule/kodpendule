"""
Session-based shopping cart (no DB models in v1).
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from django.http import HttpRequest

from apps.products.models import Product

if TYPE_CHECKING:
    pass

SESSION_KEY = "cart"


@dataclass
class CartLine:
    product: Product
    quantity: int

    @property
    def unit_price(self) -> Decimal:
        return self.product.effective_price

    @property
    def line_total(self) -> Decimal:
        return self.unit_price * self.quantity


class Cart:
    """Cart stored in the session as {product_id: quantity}."""

    def __init__(self, request: HttpRequest) -> None:
        self.request = request
        if SESSION_KEY not in request.session:
            request.session[SESSION_KEY] = {}
        self._data: dict[str, int] = request.session[SESSION_KEY]

    def _save(self) -> None:
        self.request.session[SESSION_KEY] = self._data
        self.request.session.modified = True

    def add(self, product: Product, quantity: int = 1) -> None:
        if quantity < 1:
            return
        key = str(product.pk)
        new_qty = self._data.get(key, 0) + quantity
        if new_qty > product.stock:
            raise ValueError("not_enough_stock")
        self._data[key] = new_qty
        self._save()

    def set_quantity(self, product: Product, quantity: int) -> None:
        key = str(product.pk)
        if quantity < 1:
            self.remove(product)
            return
        if quantity > product.stock:
            raise ValueError("not_enough_stock")
        self._data[key] = quantity
        self._save()

    def remove(self, product: Product) -> None:
        self._data.pop(str(product.pk), None)
        self._save()

    def clear(self) -> None:
        self._data.clear()
        self._save()

    @property
    def is_empty(self) -> bool:
        return not self._data

    @property
    def total_items(self) -> int:
        return sum(self._data.values())

    def get_lines(self) -> list[CartLine]:
        if not self._data:
            return []
        product_ids = [int(pk) for pk in self._data]
        products = {
            p.pk: p
            for p in Product.objects.filter(pk__in=product_ids).select_related("category")
        }
        lines: list[CartLine] = []
        for pk_str, qty in self._data.items():
            product = products.get(int(pk_str))
            if product and qty > 0:
                lines.append(CartLine(product=product, quantity=qty))
        return lines

    @property
    def subtotal(self) -> Decimal:
        return sum((line.line_total for line in self.get_lines()), Decimal("0"))


def get_cart(request: HttpRequest) -> Cart:
    return Cart(request)
