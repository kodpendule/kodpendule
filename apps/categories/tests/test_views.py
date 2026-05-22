import uuid
from decimal import Decimal

from django.http import Http404
from django.test import RequestFactory, TestCase

from apps.categories.models import Category
from apps.categories.selectors import get_category_by_slug
from apps.categories.views import CategoryDetailView, CategoryListView
from apps.core.tests.test_utils import apply_request_middleware
from apps.products.models import Product


class CategoryViewTests(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()
        suffix = uuid.uuid4().hex[:8]
        self.category_slug = f"satovi-{suffix}"

        self.category = Category.objects.create(is_active=True)
        self.category.set_current_language("sr")
        self.category.name = "Satovi"
        self.category.slug = self.category_slug
        self.category.description = "Svi satovi."
        self.category.save()

        self.product = Product.objects.create(
            category=self.category,
            sku=f"SKU-{suffix}",
            price=Decimal("1500.00"),
            stock=5,
            is_active=True,
        )
        self.product.set_current_language("sr")
        self.product.name = "Klasični sat"
        self.product.slug = f"klasicni-sat-{suffix}"
        self.product.save()

    def _get(self, view_class, path: str, **kwargs):
        request = self.factory.get(path)
        apply_request_middleware(request)
        return view_class.as_view()(request, **kwargs)

    def test_category_list_returns_200(self) -> None:
        response = self._get(CategoryListView, "/kategorije/")
        self.assertEqual(response.status_code, 200)

    def test_category_detail_returns_200(self) -> None:
        response = self._get(
            CategoryDetailView,
            f"/kategorije/{self.category_slug}/",
            slug=self.category_slug,
        )
        self.assertEqual(response.status_code, 200)

    def test_category_detail_404(self) -> None:
        with self.assertRaises(Http404):
            self._get(
                CategoryDetailView,
                "/kategorije/nema/",
                slug="nema",
            )

    def test_get_category_by_slug(self) -> None:
        category = get_category_by_slug(self.category_slug, "sr")
        self.assertIsNotNone(category)
        self.assertEqual(category.name, "Satovi")
