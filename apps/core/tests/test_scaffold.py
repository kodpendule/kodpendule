from django.test import SimpleTestCase

from apps.core.apps import CoreConfig


class CoreScaffoldTests(SimpleTestCase):
    def test_app_config(self) -> None:
        self.assertEqual(CoreConfig.name, "apps.core")
