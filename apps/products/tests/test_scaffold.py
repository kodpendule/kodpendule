from django.test import SimpleTestCase

from apps.products.apps import ProductsConfig


class ProductsScaffoldTests(SimpleTestCase):
    def test_app_config(self) -> None:
        self.assertEqual(ProductsConfig.name, "apps.products")
