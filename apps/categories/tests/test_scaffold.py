from django.test import SimpleTestCase

from apps.categories.apps import CategoriesConfig


class CategoriesConfigScaffoldTests(SimpleTestCase):
    def test_app_config(self) -> None:
        self.assertEqual(CategoriesConfig.name, "apps.categories")
