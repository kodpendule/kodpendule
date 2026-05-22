from decimal import Decimal

from django.test import TestCase

from apps.shipping.models import City


class CityModelTests(TestCase):
    def test_city_str(self) -> None:
        city = City.objects.create(
            name="Beograd",
            slug="beograd",
            shipping_price=Decimal("500.00"),
        )
        self.assertEqual(str(city), "Beograd")
