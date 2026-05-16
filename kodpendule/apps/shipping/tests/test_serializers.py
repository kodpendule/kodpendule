from decimal import Decimal

from django.test import TestCase

from apps.shipping.models import City
from apps.shipping.serializers import CitySerializer


class CitySerializerTests(TestCase):
    def test_serializer_output(self) -> None:
        city = City.objects.create(
            name="Novi Sad",
            slug="novi-sad",
            shipping_price=Decimal("300.00"),
        )
        data = CitySerializer(city).data
        self.assertEqual(data["name"], "Novi Sad")
        self.assertEqual(Decimal(data["shipping_price"]), Decimal("300.00"))
