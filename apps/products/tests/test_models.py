from decimal import Decimal

from django.test import TestCase

from apps.categories.models import Category
from apps.products.models import Product


class ProductModelTests(TestCase):
    def setUp(self) -> None:
        self.category = Category.objects.create()
        self.category.set_current_language("sr")
        self.category.name = "Kategorija"
        self.category.slug = "kategorija"
        self.category.save()

    def _make_product(self, **kwargs) -> Product:
        defaults = {
            "category": self.category,
            "sku": "SKU-001",
            "price": Decimal("1000.00"),
            "stock": 3,
            "minimum_stock_alert": 5,
        }
        defaults.update(kwargs)
        product = Product.objects.create(**defaults)
        product.set_current_language("sr")
        product.name = "Proizvod"
        product.slug = "proizvod"
        product.save()
        return product

    def test_effective_price_with_discount(self) -> None:
        product = self._make_product(discount_price=Decimal("800.00"))
        self.assertEqual(product.effective_price, Decimal("800.00"))
        self.assertTrue(product.has_discount)

    def test_low_stock(self) -> None:
        product = self._make_product(stock=5, minimum_stock_alert=5)
        self.assertTrue(product.is_low_stock)

    def test_not_low_stock(self) -> None:
        product = self._make_product(stock=10, minimum_stock_alert=5)
        self.assertFalse(product.is_low_stock)
