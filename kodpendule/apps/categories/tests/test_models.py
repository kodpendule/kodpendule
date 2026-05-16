from django.test import TestCase

from apps.categories.models import Category


class CategoryModelTests(TestCase):
    def test_translated_category(self) -> None:
        category = Category.objects.create(is_active=True)
        category.set_current_language("sr")
        category.name = "Satovi"
        category.slug = "satovi"
        category.save()

        category.set_current_language("en")
        category.name = "Watches"
        category.slug = "watches"
        category.save()

        category.set_current_language("sr")
        self.assertEqual(category.name, "Satovi")
