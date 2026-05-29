from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class AdminSerbianUrlTests(TestCase):
    def setUp(self) -> None:
        User = get_user_model()
        self.user = User.objects.create_superuser(
            username="adminurls",
            email="urls@test.com",
            password="testpass123",
        )

    def test_changelist_uses_serbian_slug(self) -> None:
        url = reverse("admin:products_product_changelist")
        self.assertEqual(url, "/admin/proizvodi/")

    def test_legacy_english_changelist_redirects(self) -> None:
        self.client.login(username="adminurls", password="testpass123")
        response = self.client.get("/admin/products/product/", follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/admin/proizvodi/")

    def test_serbian_changelist_renders(self) -> None:
        self.client.login(username="adminurls", password="testpass123")
        response = self.client.get("/admin/proizvodi/")
        self.assertEqual(response.status_code, 200)

    def test_dashboard_serbian_path(self) -> None:
        self.client.login(username="adminurls", password="testpass123")
        response = self.client.get(reverse("dashboard:index"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(reverse("dashboard:index"), "/admin/analitika/")
