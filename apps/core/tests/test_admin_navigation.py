from django.contrib.admin.sites import site
from django.test import RequestFactory, TestCase

from apps.core.admin_navigation import get_admin_nav_sections


class AdminNavigationTests(TestCase):
    def test_sections_include_orders_and_analytics(self):
        request = RequestFactory().get("/admin/")
        request.user = self._superuser()
        sections = get_admin_nav_sections(site.get_app_list(request), request)
        section_ids = [s.id for s in sections]
        self.assertIn("orders", section_ids)
        self.assertIn("analytics", section_ids)
        self.assertIn("products", section_ids)
        self.assertIn("users", section_ids)

        users = next(s for s in sections if s.id == "users")
        self.assertTrue(
            any("korisnici" in item.url for item in users.items),
            msg="Users section should link to the shop users changelist",
        )

        analytics = next(s for s in sections if s.id == "analytics")
        self.assertGreaterEqual(len(analytics.items), 1)
        self.assertTrue(any("analitika" in item.url for item in analytics.items))

    def test_products_section_includes_promo_sales(self):
        request = RequestFactory().get("/admin/proizvodi/")
        request.user = self._superuser()
        sections = get_admin_nav_sections(site.get_app_list(request), request)
        products = next(s for s in sections if s.id == "products")
        self.assertTrue(
            any("promo-sales" in item.url for item in products.items),
            msg="Promo sales should appear in the products sidebar section",
        )

    def test_products_section_includes_recommended_products(self):
        request = RequestFactory().get("/admin/proizvodi/")
        request.user = self._superuser()
        sections = get_admin_nav_sections(site.get_app_list(request), request)
        products = next(s for s in sections if s.id == "products")
        self.assertTrue(
            any("recommended" in item.url for item in products.items),
            msg="Recommended products should appear in the products sidebar section",
        )

    def test_recommended_page_only_highlights_recommended_item(self):
        from django.urls import reverse

        request = RequestFactory().get(reverse("admin:products_product_recommended"))
        request.user = self._superuser()
        sections = get_admin_nav_sections(site.get_app_list(request), request)
        products = next(s for s in sections if s.id == "products")
        changelist = reverse("admin:products_product_changelist")
        recommended_url = reverse("admin:products_product_recommended")

        product_item = next(item for item in products.items if item.url == changelist)
        recommended_item = next(item for item in products.items if item.url == recommended_url)

        self.assertFalse(product_item.active)
        self.assertTrue(recommended_item.active)

    def test_promo_sales_page_only_highlights_promo_item(self):
        from django.urls import reverse

        request = RequestFactory().get(reverse("admin:products_product_promo_sales"))
        request.user = self._superuser()
        sections = get_admin_nav_sections(site.get_app_list(request), request)
        products = next(s for s in sections if s.id == "products")
        changelist = reverse("admin:products_product_changelist")
        promo_url = reverse("admin:products_product_promo_sales")

        product_item = next(item for item in products.items if item.url == changelist)
        promo_item = next(item for item in products.items if item.url == promo_url)

        self.assertFalse(product_item.active)
        self.assertTrue(promo_item.active)

    def _superuser(self):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        return User.objects.create_superuser(
            username="navadmin",
            email="nav@example.com",
            password="testpass123",
        )
