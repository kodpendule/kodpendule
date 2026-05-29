import json
import re

from django.contrib.auth import get_user_model
from django.middleware.csrf import get_token
from django.test import Client, TestCase


class CategoryAdminPopupTests(TestCase):
    def setUp(self) -> None:
        user_model = get_user_model()
        self.user = user_model.objects.create_superuser(
            "popup_admin",
            "popup_admin@test.com",
            "pass",
        )
        self.client = Client()
        self.client.force_login(self.user)

    def _csrf(self) -> str:
        request = self.client.get("/admin/kategorije/add/?_popup=1").wsgi_request
        return get_token(request)

    def test_add_category_popup_returns_closing_script(self) -> None:
        slug = "popup-test-kat"
        response = self.client.post(
            "/admin/kategorije/add/?_popup=1",
            {
                "_popup": "1",
                "name_sr": "A & B",
                "name_en": "A & B EN",
                "slug_sr": slug,
                "slug_en": f"{slug}-en",
                "description_sr": "",
                "description_en": "",
                "is_active": "on",
                "sort_order": "0",
                "csrfmiddlewaretoken": self._csrf(),
            },
        )
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertIn('type="application/json"', html)
        self.assertIn("dismissAddRelatedObjectPopup", html)
        self.assertIn("window.close()", html)

        match = re.search(
            r'<script id="django-admin-popup-response-data" type="application/json">(.*?)</script>',
            html,
            re.DOTALL,
        )
        self.assertIsNotNone(match)
        data = json.loads(match.group(1))
        self.assertIn("value", data)
        self.assertEqual(data["obj"], "A & B")

        from apps.categories.models import Category

        category = Category.objects.get(pk=data["value"])
        self.assertEqual(
            category.safe_translation_getter("name", language_code="sr"),
            "A & B",
        )
