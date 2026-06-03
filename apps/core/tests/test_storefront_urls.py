import uuid

from django.conf import settings
from django.test import Client, TestCase
from django.utils import translation

from apps.categories.models import Category
from apps.core.storefront_urls import (
    resolve_storefront_route,
    shop_reverse,
    translate_storefront_url,
)
from apps.products.models import Product


class StorefrontUrlTests(TestCase):
    def tearDown(self) -> None:
        translation.deactivate()

    def test_shop_reverse_uses_serbian_paths_by_default(self) -> None:
        with translation.override("sr"):
            self.assertEqual(shop_reverse("categories:list"), "/kategorije/")
            self.assertEqual(shop_reverse("products:list"), "/proizvodi/")
            self.assertEqual(shop_reverse("core:contact"), "/kontakt/")

    def test_shop_reverse_uses_english_paths(self) -> None:
        with translation.override("en"):
            self.assertEqual(shop_reverse("categories:list"), "/categories/")
            self.assertEqual(shop_reverse("products:list"), "/products/")
            self.assertEqual(shop_reverse("core:contact"), "/contact/")

    def test_resolve_storefront_route(self) -> None:
        route = resolve_storefront_route("/categories/")
        self.assertIsNotNone(route)
        assert route is not None
        self.assertEqual(route.viewname, "categories:list")
        self.assertEqual(route.language, "en")

    def test_translate_storefront_url_between_languages(self) -> None:
        self.assertEqual(
            translate_storefront_url("/kategorije/", "en"),
            "/categories/",
        )
        self.assertEqual(
            translate_storefront_url("/categories/", "sr"),
            "/kategorije/",
        )

    def test_shop_reverse_legal_pages(self) -> None:
        with translation.override("sr"):
            self.assertEqual(shop_reverse("core:terms"), "/uslovi-koriscenja/")
            self.assertEqual(shop_reverse("core:privacy"), "/politika-privatnosti/")
        with translation.override("en"):
            self.assertEqual(shop_reverse("core:terms"), "/terms-of-service/")
            self.assertEqual(shop_reverse("core:privacy"), "/privacy-policy/")

    def test_middleware_redirects_wrong_language_path(self) -> None:
        client = Client()
        client.cookies[settings.LANGUAGE_COOKIE_NAME] = "en"
        response = client.get("/kategorije/")
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response["Location"], "/categories/")

    def test_middleware_does_not_redirect_post_checkout(self) -> None:
        client = Client()
        client.cookies[settings.LANGUAGE_COOKIE_NAME] = "en"
        response = client.post("/placanje/", {})
        self.assertNotEqual(response.status_code, 301)
        self.assertNotEqual(response.get("Location"), "/checkout/")

    def test_language_switch_translates_next_url(self) -> None:
        client = Client()
        response = client.post(
            "/jezik/",
            {"language": "en", "next": "/kategorije/"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/categories/")
        self.assertEqual(client.cookies[settings.LANGUAGE_COOKIE_NAME].value, "en")

    def test_category_detail_uses_localized_path_on_switch(self) -> None:
        category = Category.objects.create(is_active=True)
        category.set_current_language("sr")
        category.name = "Alkoholna pica"
        category.slug = "alkoholna-pica"
        category.save()
        category.set_current_language("en")
        category.name = "Alcoholic drinks"
        category.slug = "alcoholic-drinks"
        category.save()

        client = Client()
        response = client.post(
            "/jezik/",
            {"language": "en", "next": "/kategorije/alkoholna-pica/"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/categories/alcoholic-drinks/")

    def test_product_get_absolute_url_respects_language(self) -> None:
        category = Category.objects.create(is_active=True)
        category.set_current_language("sr")
        category.name = "Cat"
        category.slug = "cat-sr"
        category.save()

        product = Product.objects.create(
            category=category,
            sku="SKU-1",
            price="100.00",
            stock=1,
        )
        product.set_current_language("sr")
        product.name = "Proizvod"
        product.slug = "proizvod-sr"
        product.save()
        product.set_current_language("en")
        product.name = "Product"
        product.slug = "product-en"
        product.save()

        with translation.override("en"):
            self.assertEqual(product.get_absolute_url(), "/products/product-en/")
