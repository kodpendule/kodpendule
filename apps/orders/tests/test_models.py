from decimal import Decimal

from django.test import TestCase

from apps.orders.models import Order, OrderItem, OrderStatus, PaymentMethod
from apps.shipping.models import City


class OrderModelTests(TestCase):
    def setUp(self) -> None:
        self.city = City.objects.create(
            name="Novi Sad",
            slug="novi-sad",
            shipping_price=Decimal("300.00"),
        )

    def _create_guest_order(self) -> Order:
        return Order.objects.create(
            order_number="KP-20260516-0001",
            guest_email="guest@example.com",
            first_name="Milan",
            last_name="Petrović",
            phone="+381601112233",
            shipping_street="Ulica 1",
            shipping_city_name="Novi Sad",
            shipping_postal_code="21000",
            shipping_city=self.city,
            billing_street="Ulica 1",
            billing_city_name="Novi Sad",
            billing_postal_code="21000",
            order_notes="Pozvati pre dostave.",
            shipping_price=Decimal("300.00"),
            payment_method=PaymentMethod.COD,
            status=OrderStatus.PENDING,
            subtotal=Decimal("2000.00"),
            total=Decimal("2300.00"),
        )

    def test_guest_order(self) -> None:
        order = self._create_guest_order()
        self.assertTrue(order.is_guest_order)
        self.assertEqual(order.customer_email, "guest@example.com")

    def test_order_item_line_total(self) -> None:
        order = self._create_guest_order()
        item = OrderItem.objects.create(
            order=order,
            product_name="Test product",
            sku="SKU-1",
            unit_price=Decimal("500.00"),
            quantity=2,
        )
        self.assertEqual(item.line_total, Decimal("1000.00"))
