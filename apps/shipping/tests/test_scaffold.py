from django.test import SimpleTestCase

from apps.shipping.apps import ShippingConfig


class ShippingConfigScaffoldTests(SimpleTestCase):
    def test_app_config(self) -> None:
        self.assertEqual(ShippingConfig.name, "apps.shipping")
