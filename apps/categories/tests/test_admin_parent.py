import uuid

from django.contrib.auth import get_user_model
from django.middleware.csrf import get_token
from django.test import Client, TestCase
from django.urls import reverse

from apps.categories.models import Category


class CategoryAdminParentTests(TestCase):
    def setUp(self) -> None:
        user_model = get_user_model()
        suffix = uuid.uuid4().hex[:8]
        self.user = user_model.objects.create_superuser(
            f"cat_admin_{suffix}",
            f"cat_admin_{suffix}@test.com",
            "pass",
        )
        self.client = Client()
        self.client.force_login(self.user)

        self.parent = Category.objects.create(is_active=True)
        self.parent.set_current_language("sr")
        self.parent.name = "Roditelj"
        self.parent.slug = f"roditelj-{suffix}"
        self.parent.save()

    def _csrf(self) -> str:
        request = self.client.get(reverse("admin:categories_category_add")).wsgi_request
        return get_token(request)

    def test_create_child_category_with_parent(self) -> None:
        suffix = uuid.uuid4().hex[:8]
        slug = f"dete-{suffix}"
        response = self.client.post(
            reverse("admin:categories_category_add"),
            {
                "parent": str(self.parent.pk),
                "is_active": "on",
                "sort_order": "0",
                "name_sr": "Dete",
                "slug_sr": slug,
                "name_en": "",
                "slug_en": "",
                "description_sr": "",
                "description_en": "",
                "meta_title_sr": "",
                "meta_title_en": "",
                "meta_description_sr": "",
                "meta_description_en": "",
                "csrfmiddlewaretoken": self._csrf(),
            },
        )
        self.assertEqual(response.status_code, 302, response.content[:500])
        child = Category.objects.get(translations__slug=slug)
        self.assertEqual(child.parent_id, self.parent.pk)
        self.assertFalse(child.translations.filter(language_code="en").exists())

    def test_create_second_category_without_english_translation(self) -> None:
        """Regression: empty EN slug must not violate unique constraint."""
        suffix = uuid.uuid4().hex[:8]
        for index, slug in enumerate((f"kat-a-{suffix}", f"kat-b-{suffix}")):
            response = self.client.post(
                reverse("admin:categories_category_add"),
                {
                    "parent": "",
                    "is_active": "on",
                    "sort_order": str(index),
                    "name_sr": f"Kat {index}",
                    "slug_sr": slug,
                    "name_en": "",
                    "slug_en": "",
                    "description_sr": "",
                    "description_en": "",
                    "meta_title_sr": "",
                    "meta_title_en": "",
                    "meta_description_sr": "",
                    "meta_description_en": "",
                    "csrfmiddlewaretoken": self._csrf(),
                },
            )
            self.assertEqual(response.status_code, 302, response.content[:500])
        self.assertEqual(Category.objects.filter(translations__language_code="sr").count(), 3)

    def test_create_category_with_duplicate_slugs_in_both_languages(self) -> None:
        suffix = uuid.uuid4().hex[:8]
        slug = f"duplikat-{suffix}"
        response = self.client.post(
            reverse("admin:categories_category_add"),
            {
                "parent": "",
                "is_active": "on",
                "sort_order": "0",
                "name_sr": "Duplikat",
                "slug_sr": slug,
                "name_en": "Duplicate",
                "slug_en": slug,
                "description_sr": "",
                "description_en": "",
                "meta_title_sr": "",
                "meta_title_en": "",
                "meta_description_sr": "",
                "meta_description_en": "",
                "csrfmiddlewaretoken": self._csrf(),
            },
        )
        self.assertEqual(response.status_code, 302, response.content[:500])
        category = Category.objects.get(translations__slug=slug)
        en_slug = category.safe_translation_getter("slug", language_code="en")
        self.assertNotEqual(en_slug, slug)

    def test_create_category_with_same_name_in_both_languages(self) -> None:
        suffix = uuid.uuid4().hex[:8]
        response = self.client.post(
            reverse("admin:categories_category_add"),
            {
                "parent": "",
                "is_active": "on",
                "sort_order": "0",
                "name_sr": f"Isto ime {suffix}",
                "slug_sr": "",
                "name_en": f"Isto ime {suffix}",
                "slug_en": "",
                "description_sr": "",
                "description_en": "",
                "meta_title_sr": "",
                "meta_title_en": "",
                "meta_description_sr": "",
                "meta_description_en": "",
                "csrfmiddlewaretoken": self._csrf(),
            },
        )
        self.assertEqual(response.status_code, 302, response.content[:500])
        category = Category.objects.order_by("-pk").first()
        sr_slug = category.safe_translation_getter("slug", language_code="sr")
        en_slug = category.safe_translation_getter("slug", language_code="en")
        self.assertTrue(sr_slug)
        self.assertTrue(en_slug)
        self.assertNotEqual(sr_slug, en_slug)
