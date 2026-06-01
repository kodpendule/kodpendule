import uuid
from decimal import Decimal
from io import BytesIO

from types import SimpleNamespace

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase

from apps.categories.models import Category
from apps.products.admin import ProductAdmin, ProductImageInline
from apps.products.models import Product, ProductImage


class ProductAdminMainImageTests(TestCase):
    def setUp(self) -> None:
        suffix = uuid.uuid4().hex[:8]
        category = Category.objects.create(is_active=True)
        category.set_current_language("sr")
        category.name = "Kat"
        category.slug = f"kat-{suffix}"
        category.save()

        self.product = Product.objects.create(
            category=category,
            sku=f"SKU-{suffix}",
            price=Decimal("1000.00"),
            stock=5,
        )
        self.product.set_current_language("sr")
        self.product.name = "Proizvod"
        self.product.slug = f"proizvod-{suffix}"
        self.product.save()

        user = get_user_model().objects.create_superuser(
            f"img_admin_{suffix}",
            f"img_admin_{suffix}@test.com",
            "pass",
        )
        self.request = RequestFactory().get("/admin/")
        self.request.user = user

    def test_save_formset_skips_empty_gallery_rows(self) -> None:
        main_file = SimpleUploadedFile(
            "main.jpg",
            BytesIO(b"main-image").getvalue(),
            content_type="image/jpeg",
        )
        self.product.main_image = main_file
        self.product.save()

        product_admin = ProductAdmin(Product, admin.site)
        inline = ProductImageInline(Product, admin.site)
        formset_class = inline.get_formset(self.request)
        formset = formset_class(
            instance=self.product,
            data={
                "gallery_images-TOTAL_FORMS": "1",
                "gallery_images-INITIAL_FORMS": "0",
                "gallery_images-MIN_NUM_FORMS": "0",
                "gallery_images-MAX_NUM_FORMS": "1000",
                "gallery_images-0-image": "",
                "gallery_images-0-alt_text_sr": "",
                "gallery_images-0-alt_text_en": "",
                "gallery_images-0-sort_order": "0",
            },
        )
        self.assertTrue(formset.is_valid(), formset.errors)
        product_form = SimpleNamespace(instance=self.product)
        product_admin.save_formset(self.request, form=product_form, formset=formset, change=True)

        self.product.refresh_from_db()
        self.assertTrue(self.product.main_image)
        self.assertEqual(self.product.gallery_images.count(), 0)

    def test_duplicate_gallery_path_matching_main_is_removed(self) -> None:
        main_file = SimpleUploadedFile(
            "main.jpg",
            BytesIO(b"main-image").getvalue(),
            content_type="image/jpeg",
        )
        self.product.main_image = main_file
        self.product.save()
        main_name = self.product.main_image.name

        ProductImage.objects.create(
            product=self.product,
            image=main_name,
            sort_order=0,
        )
        ProductImage.objects.create(
            product=self.product,
            image=SimpleUploadedFile(
                "gallery.jpg",
                BytesIO(b"gallery").getvalue(),
                content_type="image/jpeg",
            ),
            sort_order=1,
        )

        product_admin = ProductAdmin(Product, admin.site)
        inline = ProductImageInline(Product, admin.site)
        formset_class = inline.get_formset(self.request)
        formset = formset_class(instance=self.product)
        product_form = SimpleNamespace(instance=self.product)
        product_admin.save_formset(self.request, form=product_form, formset=formset, change=True)

        self.assertTrue(self.product.main_image)
        self.assertEqual(self.product.gallery_images.count(), 1)
        self.assertNotEqual(self.product.gallery_images.get().image.name, main_name)
