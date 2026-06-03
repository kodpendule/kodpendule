import uuid

from django.test import TestCase

from apps.categories.models import Category
from apps.core.slugs import unique_slug_for_translation


class UniqueSlugForTranslationTests(TestCase):
    def test_reserved_slugs_avoid_batch_collision(self) -> None:
        category = Category.objects.create(is_active=True)
        sr = category.translations.model(master=category, language_code="sr", name="Piće")
        en = category.translations.model(master=category, language_code="en", name="Piće")

        sr.slug = unique_slug_for_translation(sr)
        en.slug = unique_slug_for_translation(en, reserved={sr.slug})

        self.assertNotEqual(sr.slug, en.slug)
        self.assertTrue(en.slug.startswith(f"{sr.slug}-"))

    def test_base_override_avoids_existing_slug(self) -> None:
        suffix = uuid.uuid4().hex[:8]
        existing = Category.objects.create(is_active=True)
        existing.set_current_language("sr")
        existing.name = "Existing"
        existing.slug = f"pice-{suffix}"
        existing.save()

        category = Category.objects.create(is_active=True)
        trans = category.translations.model(
            master=category,
            language_code="sr",
            name="Piće",
        )
        trans.slug = unique_slug_for_translation(
            trans,
            base_override=f"pice-{suffix}",
        )
        self.assertNotEqual(trans.slug, f"pice-{suffix}")
