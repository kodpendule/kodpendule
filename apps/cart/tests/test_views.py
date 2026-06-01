import json
import uuid
from decimal import Decimal

from django.test import Client, TestCase

from apps.cart.cart import SESSION_KEY, get_cart
from apps.categories.models import Category
from apps.core.storefront_urls import shop_reverse
from apps.products.models import Product


class CartUpdateViewTests(TestCase):
    def setUp(self) -> None:
        suffix = uuid.uuid4().hex[:8]
        self.category = Category.objects.create(is_active=True)
        self.category.set_current_language("sr")
        self.category.name = "Kat"
        self.category.slug = f"kat-{suffix}"
        self.category.save()

        self.product = Product.objects.create(
            category=self.category,
            sku=f"SKU-CART-{suffix}",
            price=Decimal("500.00"),
            stock=5,
        )
        self.product.set_current_language("sr")
        self.product.name = "Cart product"
        self.product.slug = f"cart-{suffix}"
        self.product.save()

        self.client = Client()
        session = self.client.session
        session[SESSION_KEY] = {str(self.product.pk): 1}
        session.save()

    def test_cart_update_returns_json_totals(self) -> None:
        url = shop_reverse("cart:update", product_id=self.product.pk)
        response = self.client.post(
            url,
            {"quantity": 3},
            HTTP_ACCEPT="application/json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["subtotal"], "1500.00")
        self.assertEqual(payload["item_count"], 3)
        self.assertEqual(payload["lines"][0]["quantity"], 3)
        self.assertEqual(payload["lines"][0]["line_total"], "1500.00")

    def test_cart_update_json_rejects_over_stock(self) -> None:
        url = shop_reverse("cart:update", product_id=self.product.pk)
        response = self.client.post(
            url,
            {"quantity": 99},
            HTTP_ACCEPT="application/json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 400)
        payload = json.loads(response.content)
        self.assertFalse(payload["ok"])
        self.assertIn("error", payload)

    def test_cart_page_includes_live_update_script(self) -> None:
        response = self.client.get(shop_reverse("cart:detail"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "data-cart-page")
        self.assertContains(response, "cart.js")
        self.assertNotContains(response, "shop-cart-line__update")


class CartAddViewTests(TestCase):
    def setUp(self) -> None:
        suffix = uuid.uuid4().hex[:8]
        category = Category.objects.create(is_active=True)
        category.set_current_language("sr")
        category.name = "Kat"
        category.slug = f"kat-add-{suffix}"
        category.save()

        self.product = Product.objects.create(
            category=category,
            sku=f"SKU-ADD-{suffix}",
            price=Decimal("500.00"),
            stock=5,
        )
        self.product.set_current_language("sr")
        self.product.name = "Add product"
        self.product.slug = f"add-{suffix}"
        self.product.save()

    def test_add_from_list_with_quantity(self) -> None:
        response = self.client.post(
            shop_reverse("cart:add"),
            {
                "product_id": self.product.pk,
                "quantity": 3,
                "next": shop_reverse("products:list"),
            },
        )
        self.assertEqual(response.status_code, 302)
        cart = get_cart(self.client)
        lines = cart.get_lines()
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0].quantity, 3)
        self.assertEqual(lines[0].product.pk, self.product.pk)
