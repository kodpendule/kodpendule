from django.db import IntegrityError
from django.test import TestCase

from apps.newsletter.models import Subscriber


class SubscriberModelTests(TestCase):
    def test_unique_email(self) -> None:
        Subscriber.objects.create(email="buyer@example.com")
        with self.assertRaises(IntegrityError):
            Subscriber.objects.create(email="buyer@example.com")
