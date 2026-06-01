import uuid
from decimal import Decimal

from django.test import TestCase

from apps.categories.models import Category
from apps.core.storefront_urls import shop_reverse
from apps.products.models import Product


class HomeFeaturedProductTests(TestCase):
    def test_featured_product_uses_recommended_not_newest(self) -> None:
        suffix = uuid.uuid4().hex[:8]
        category = Category.objects.create(is_active=True)
        category.set_current_language("sr")
        category.name = "Pića"
        category.slug = f"pica-{suffix}"
        category.save()

        newest = Product.objects.create(
            category=category,
            sku=f"NEW-{suffix}",
            price=Decimal("100.00"),
            stock=5,
        )
        newest.set_current_language("sr")
        newest.name = "Rosa 1.5L"
        newest.slug = f"rosa-{suffix}"
        newest.save()

        recommended = Product.objects.create(
            category=category,
            sku=f"REC-{suffix}",
            price=Decimal("200.00"),
            stock=5,
            is_recommended=True,
            recommended_order=0,
        )
        recommended.set_current_language("sr")
        recommended.name = "Staff pick"
        recommended.slug = f"staff-{suffix}"
        recommended.save()

        response = self.client.get(shop_reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        featured = response.context["featured_product"]
        self.assertIsNone(featured)

    def test_featured_product_is_first_recommended_with_image(self) -> None:
        suffix = uuid.uuid4().hex[:8]
        category = Category.objects.create(is_active=True)
        category.set_current_language("sr")
        category.name = "Pića"
        category.slug = f"pica2-{suffix}"
        category.save()

        from django.core.files.uploadedfile import SimpleUploadedFile

        image = SimpleUploadedFile(
            "pick.jpg",
            b"fake-image-bytes",
            content_type="image/jpeg",
        )
        recommended = Product.objects.create(
            category=category,
            sku=f"REC2-{suffix}",
            price=Decimal("200.00"),
            stock=5,
            is_recommended=True,
            recommended_order=0,
            main_image=image,
        )
        recommended.set_current_language("sr")
        recommended.name = "Staff pick with image"
        recommended.slug = f"staff2-{suffix}"
        recommended.save()

        response = self.client.get(shop_reverse("core:home"))
        featured = response.context["featured_product"]
        self.assertIsNotNone(featured)
        assert featured is not None
        self.assertEqual(featured.pk, recommended.pk)

    def test_homepage_shows_categories_after_hero(self) -> None:
        suffix = uuid.uuid4().hex[:8]
        category = Category.objects.create(is_active=True, sort_order=0)
        category.set_current_language("sr")
        category.name = "Alkoholna pića"
        category.slug = f"alkoholna-pica-{suffix}"
        category.save()

        response = self.client.get(shop_reverse("core:home"))
        content = response.content.decode()
        hero_pos = content.find('class="shop-hero')
        categories_pos = content.find('id="home-categories"')
        trust_pos = content.find('class="shop-home-trust')
        self.assertGreater(categories_pos, hero_pos)
        self.assertGreater(trust_pos, categories_pos)
        self.assertContains(response, 'href="#home-categories"')
        self.assertContains(response, "Poruči odmah")
        self.assertContains(response, "Alkoholna pića")
