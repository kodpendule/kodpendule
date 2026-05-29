from decimal import Decimal

from django.test import TestCase

from apps.shipping.models import City, ShippingMethod


class CityModelTests(TestCase):
    def test_city_str(self) -> None:
        city = City.objects.create(
            name="Beograd",
            slug="beograd",
            shipping_price=Decimal("500.00"),
        )
        self.assertEqual(str(city), "Beograd")


class ShippingMethodModelTests(TestCase):
    def test_localized_name_uses_language_with_fallback(self) -> None:
        method = ShippingMethod.objects.create(
            name_sr="Dostava kurirskom službom",
            name_en="Courier delivery",
        )
        self.assertEqual(method.localized_name("sr"), "Dostava kurirskom službom")
        self.assertEqual(method.localized_name("en"), "Courier delivery")

    def test_localized_name_falls_back_to_serbian_when_english_empty(self) -> None:
        method = ShippingMethod.objects.create(name_sr="Lično preuzimanje")
        self.assertEqual(method.localized_name("en"), "Lično preuzimanje")

    def test_str_uses_localized_name(self) -> None:
        method = ShippingMethod.objects.create(
            name_sr="Standard",
            name_en="Standard EN",
        )
        self.assertEqual(str(method), "Standard")
