from django.test import SimpleTestCase

from apps.orders.apps import OrdersConfig


class OrdersConfigScaffoldTests(SimpleTestCase):
    def test_app_config(self) -> None:
        self.assertEqual(OrdersConfig.name, "apps.orders")
