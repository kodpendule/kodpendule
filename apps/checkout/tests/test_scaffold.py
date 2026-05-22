from django.test import SimpleTestCase

from apps.checkout.apps import CheckoutConfig


class CheckoutConfigScaffoldTests(SimpleTestCase):
    def test_app_config(self) -> None:
        self.assertEqual(CheckoutConfig.name, "apps.checkout")
