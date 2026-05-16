from django.test import SimpleTestCase

from apps.cart.apps import CartConfig


class CartConfigScaffoldTests(SimpleTestCase):
    def test_app_config(self) -> None:
        self.assertEqual(CartConfig.name, "apps.cart")
