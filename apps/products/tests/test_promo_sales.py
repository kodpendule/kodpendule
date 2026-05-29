import uuid
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from apps.categories.models import Category
from apps.products.models import Product


class PromoSalesAdminTests(TestCase):
    def setUp(self) -> None:
        suffix = uuid.uuid4().hex[:8]
        self.category = Category.objects.create(is_active=True)
        self.category.set_current_language("sr")
        self.category.name = "Kat"
        self.category.slug = f"kat-{suffix}"
        self.category.save()

        self.product = Product.objects.create(
            category=self.category,
            sku=f"PROMO-{suffix}",
            price=Decimal("1000.00"),
            discount_price=Decimal("850.00"),
            stock=5,
        )
        self.product.set_current_language("sr")
        self.product.name = f"Promo product {suffix}"
        self.product.slug = f"promo-product-{suffix}"
        self.product.save()

        admin = get_user_model().objects.create_superuser("admin", "a@test.com", "pass")
        self.client = Client()
        self.client.force_login(admin)
        self.url = reverse("admin:products_product_promo_sales")

    def test_remove_promo_clears_discount_price(self) -> None:
        response = self.client.post(
            self.url,
            {
                "action": "remove",
                "products": [str(self.product.pk)],
            },
        )
        self.assertEqual(response.status_code, 302)

        self.product.refresh_from_db()
        self.assertIsNone(self.product.discount_price)
        self.assertFalse(self.product.has_discount)

    def test_apply_promo_sets_discount_price(self) -> None:
        self.product.discount_price = None
        self.product.save(update_fields=["discount_price"])

        response = self.client.post(
            self.url,
            {
                "action": "apply",
                "products": [str(self.product.pk)],
                "discount_percent": "20",
            },
        )
        self.assertEqual(response.status_code, 302)

        self.product.refresh_from_db()
        self.assertEqual(self.product.discount_price, Decimal("800.00"))
        self.assertTrue(self.product.has_discount)

    def test_homepage_promo_query_excludes_cleared_products(self) -> None:
        from django.db.models import F

        self.client.post(
            self.url,
            {
                "action": "remove",
                "products": [str(self.product.pk)],
            },
        )

        promo_qs = Product.objects.filter(
            discount_price__isnull=False,
            discount_price__lt=F("price"),
        )
        self.assertFalse(promo_qs.filter(pk=self.product.pk).exists())
