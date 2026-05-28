import uuid
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from apps.categories.models import Category
from apps.core.views import RECOMMENDED_PRODUCTS_PER_PAGE
from apps.products.models import Product
from apps.products.selectors import recommended_products_qs


class RecommendedProductsTests(TestCase):
    def setUp(self) -> None:
        suffix = uuid.uuid4().hex[:8]
        self.category = Category.objects.create(is_active=True)
        self.category.set_current_language("sr")
        self.category.name = "Kat"
        self.category.slug = f"kat-{suffix}"
        self.category.save()

        self.product_a = self._create_product(f"A-{suffix}", recommended=True, order=0)
        self.product_b = self._create_product(f"B-{suffix}", recommended=True, order=1)
        self.product_c = self._create_product(f"C-{suffix}", recommended=False, order=0)

    def _create_product(self, sku: str, *, recommended: bool, order: int) -> Product:
        product = Product.objects.create(
            category=self.category,
            sku=sku,
            price=Decimal("1000.00"),
            stock=5,
            is_recommended=recommended,
            recommended_order=order,
        )
        product.set_current_language("sr")
        product.name = f"Product {sku}"
        product.slug = f"product-{sku.lower()}"
        product.save()
        return product

    def test_recommended_selector_filters_and_orders(self) -> None:
        products = list(recommended_products_qs("sr"))
        self.assertEqual(len(products), 2)
        self.assertEqual(products[0].pk, self.product_a.pk)
        self.assertEqual(products[1].pk, self.product_b.pk)

    def test_admin_recommended_view_updates_flags(self) -> None:
        User = get_user_model()
        admin = User.objects.create_superuser("admin", "a@test.com", "pass")
        client = Client()
        client.force_login(admin)

        url = reverse("admin:products_product_recommended")
        response = client.post(
            url,
            {"recommended": [str(self.product_c.pk)]},
        )
        self.assertEqual(response.status_code, 302)

        self.product_a.refresh_from_db()
        self.product_b.refresh_from_db()
        self.product_c.refresh_from_db()
        self.assertFalse(self.product_a.is_recommended)
        self.assertFalse(self.product_b.is_recommended)
        self.assertTrue(self.product_c.is_recommended)
        self.assertEqual(self.product_c.recommended_order, 0)

    def test_home_shows_recommended_section(self) -> None:
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "home-section-recommended")
        self.assertContains(response, "data-recommended-carousel")
        self.assertContains(response, self.product_a.name)

    def test_home_paginates_five_per_page(self) -> None:
        suffix = uuid.uuid4().hex[:8]
        for index in range(6):
            self._create_product(f"X{index}-{suffix}", recommended=True, order=index + 2)

        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        pages = response.context["recommended_product_pages"]
        self.assertEqual(len(pages), 2)
        self.assertEqual(len(pages[0]), RECOMMENDED_PRODUCTS_PER_PAGE)
        self.assertEqual(len(pages[1]), 3)
