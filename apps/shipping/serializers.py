from rest_framework import serializers

from apps.shipping.models import City


class CitySerializer(serializers.ModelSerializer):
    """Read-only city + shipping price for checkout AJAX."""

    class Meta:
        model = City
        fields = ("id", "name", "slug", "shipping_price")
        read_only_fields = fields
