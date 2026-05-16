from django.test import SimpleTestCase

from apps.newsletter.apps import NewsletterConfig


class NewsletterConfigScaffoldTests(SimpleTestCase):
    def test_app_config(self) -> None:
        self.assertEqual(NewsletterConfig.name, "apps.newsletter")
