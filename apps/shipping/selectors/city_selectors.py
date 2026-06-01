from django.db.models import QuerySet

from apps.shipping.models import City


def active_cities() -> QuerySet[City]:
    return City.objects.filter(is_active=True)
