from __future__ import annotations

import secrets
from datetime import date
from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.accounts.services import archive_customer_from_checkout
from apps.cart.cart import Cart, CartLine
from apps.orders.models import Order, OrderItem, OrderStatus, PaymentMethod
from apps.orders.payments.cod import CashOnDeliveryProvider
from apps.products.models import Product
from apps.shipping.models import City
from apps.shipping.selectors import get_default_shipping_method


class CheckoutError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


def generate_order_number() -> str:
    stamp = timezone.localdate().strftime("%Y%m%d")
    suffix = secrets.token_hex(3).upper()
    return f"KP-{stamp}-{suffix}"


@transaction.atomic
def create_order_from_checkout(
    *,
    cart: Cart,
    user,
    guest_email: str,
    first_name: str,
    last_name: str,
    phone: str,
    shipping_city: City,
    shipping_street: str,
    shipping_postal_code: str,
    billing_street: str,
    billing_city_name: str,
    billing_postal_code: str,
    order_notes: str,
    delivery_date: date | None,
    flexible_delivery: bool,
) -> Order:
    lines = cart.get_lines()
    if not lines:
        raise CheckoutError(_("Your cart is empty."))

    _validate_stock(lines)

    subtotal = cart.subtotal
    shipping_price = shipping_city.shipping_price
    total = subtotal + shipping_price

    email = guest_email
    if user and user.is_authenticated and user.email:
        email = user.email or guest_email

    order = Order.objects.create(
        order_number=generate_order_number(),
        user=user if user and user.is_authenticated else None,
        guest_email=email,
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        shipping_street=shipping_street,
        shipping_city_name=shipping_city.name,
        shipping_postal_code=shipping_postal_code,
        shipping_city=shipping_city,
        billing_street=billing_street,
        billing_city_name=billing_city_name,
        billing_postal_code=billing_postal_code,
        order_notes=order_notes,
        delivery_date=delivery_date,
        flexible_delivery=flexible_delivery,
        shipping_method=get_default_shipping_method(),
        shipping_price=shipping_price,
        payment_method=PaymentMethod.COD,
        status=OrderStatus.PENDING,
        subtotal=subtotal,
        total=total,
    )

    for line in lines:
        product = Product.objects.select_for_update().get(pk=line.product.pk)
        if product.stock < line.quantity:
            raise CheckoutError(
                _("Not enough stock for %(name)s.")
                % {
                    "name": product.safe_translation_getter("name", any_language=True)
                    or product.sku
                }
            )
        product.stock -= line.quantity
        product.save(update_fields=["stock"])

        OrderItem.objects.create(
            order=order,
            product=product,
            product_name=product.safe_translation_getter("name", any_language=True)
            or product.sku,
            sku=product.sku,
            unit_price=line.unit_price,
            quantity=line.quantity,
        )

    provider = CashOnDeliveryProvider()
    result = provider.charge(order)
    if not result.success:
        raise CheckoutError(result.message)

    archive_customer_from_checkout(
        email=email,
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        user=user,
    )

    cart.clear()
    return order


def _validate_stock(lines: list[CartLine]) -> None:
    for line in lines:
        if line.quantity > line.product.stock:
            raise CheckoutError(
                _("Not enough stock for %(name)s.")
                % {
                    "name": line.product.safe_translation_getter("name", any_language=True)
                    or line.product.sku
                }
            )
