import uuid
from decimal import Decimal

from django.test import RequestFactory, TestCase

from apps.cart.cart import get_cart
from apps.categories.models import Category
from apps.checkout.forms import CheckoutForm
from apps.orders.models import Order
from apps.orders.services import create_order_from_checkout
from apps.products.models import Product
from apps.shipping.models import City


class CheckoutServiceTests(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.request = self.factory.get("/")
        self.request.session = self.client.session

        self.city = City.objects.create(
            name="Beograd",
            slug="beograd",
            shipping_price=Decimal("350.00"),
            is_active=True,
        )

        suffix = uuid.uuid4().hex[:8]
        category = Category.objects.create(is_active=True)
        category.set_current_language("sr")
        category.name = "Kat"
        category.slug = f"kat-{suffix}"
        category.save()

        self.product = Product.objects.create(
            category=category,
            sku=f"SKU-CHK-{suffix}",
            price=Decimal("2000.00"),
            stock=10,
            is_active=True,
        )
        self.product.set_current_language("sr")
        self.product.name = "Checkout product"
        self.product.slug = f"chk-{suffix}"
        self.product.save()

        cart = get_cart(self.request)
        cart.add(self.product, 1)

    def test_create_order_from_checkout(self) -> None:
        cart = get_cart(self.request)
        order = create_order_from_checkout(
            cart=cart,
            user=None,
            guest_email="guest@example.com",
            first_name="Pera",
            last_name="Perić",
            phone="+381601112233",
            shipping_city=self.city,
            shipping_street="Ulica 1",
            shipping_postal_code="11000",
            billing_street="Ulica 1",
            billing_city_name="Beograd",
            billing_postal_code="11000",
            order_notes="Pozvati pre dostave.",
            delivery_date=None,
            flexible_delivery=True,
        )
        self.assertTrue(order.order_number.startswith("KP-"))
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.total, Decimal("2350.00"))
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 9)
        self.assertTrue(get_cart(self.request).is_empty)

    def test_checkout_form_requires_notes(self) -> None:
        form = CheckoutForm(
            data={
                "guest_email": "a@b.rs",
                "first_name": "A",
                "last_name": "B",
                "phone": "123",
                "shipping_city": self.city.pk,
                "shipping_street": "St",
                "shipping_postal_code": "11000",
                "billing_same_as_shipping": True,
                "order_notes": "",
            },
            user=None,
        )
        self.assertFalse(form.is_valid())
