import uuid
from decimal import Decimal

from django.test import RequestFactory, TestCase

from apps.cart.cart import get_cart
from apps.categories.models import Category
from apps.products.models import Product


class CartTests(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.request = self.factory.get("/")
        self.request.session = self.client.session

        suffix = uuid.uuid4().hex[:8]
        self.category = Category.objects.create(is_active=True)
        self.category.set_current_language("sr")
        self.category.name = "Kat"
        self.category.slug = f"kat-{suffix}"
        self.category.save()

        self.product = Product.objects.create(
            category=self.category,
            sku=f"SKU-CART-{suffix}",
            price=Decimal("500.00"),
            stock=5,
        )
        self.product.set_current_language("sr")
        self.product.name = "Cart product"
        self.product.slug = f"cart-{suffix}"
        self.product.save()

    def test_add_and_subtotal(self) -> None:
        cart = get_cart(self.request)
        cart.add(self.product, 2)
        self.assertEqual(cart.total_items, 2)
        self.assertEqual(cart.subtotal, Decimal("1000.00"))

    def test_remove_clears_line(self) -> None:
        cart = get_cart(self.request)
        cart.add(self.product, 1)
        cart.remove(self.product)
        self.assertTrue(cart.is_empty)
