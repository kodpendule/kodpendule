from django.db.models import QuerySet

from apps.shipping.models import City, ShippingMethod


def active_cities() -> QuerySet[City]:
    return City.objects.filter(is_active=True).order_by("sort_order", "name")


def get_default_shipping_method() -> ShippingMethod | None:
    return (
        ShippingMethod.objects.filter(is_active=True, is_default=True).first()
        or ShippingMethod.objects.filter(is_active=True).first()
    )
