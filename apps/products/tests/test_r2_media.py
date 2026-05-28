from io import BytesIO
from unittest.mock import MagicMock, patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from apps.categories.models import Category
from apps.core.r2_media import delete_file_from_r2
from apps.products.models import Product, ProductImage


@override_settings(
    USE_R2=True,
    AWS_ACCESS_KEY_ID="key",
    AWS_SECRET_ACCESS_KEY="secret",
    AWS_STORAGE_BUCKET_NAME="bucket",
    AWS_S3_ENDPOINT_URL="https://example.r2.cloudflarestorage.com",
    AWS_LOCATION="media",
)
class R2MediaDeletionTests(TestCase):
    @patch("apps.core.r2_media.boto3.client")
    def test_delete_file_from_r2_builds_key(self, client_mock) -> None:
        s3 = MagicMock()
        client_mock.return_value = s3

        delete_file_from_r2("products/photo.jpg")

        s3.delete_object.assert_called_once_with(
            Bucket="bucket",
            Key="media/products/photo.jpg",
        )

    @patch("apps.core.r2_media.boto3.client")
    def test_delete_file_from_r2_noop_when_disabled(self, client_mock) -> None:
        with self.settings(USE_R2=False):
            delete_file_from_r2("products/photo.jpg")
        client_mock.assert_not_called()

    @patch("apps.core.r2_media.delete_file_from_r2")
    def test_product_delete_removes_main_and_gallery(self, delete_mock) -> None:
        category = Category.objects.create(is_active=True)
        category.set_current_language("sr")
        category.name = "Kat"
        category.slug = "kat"
        category.save()

        product = Product.objects.create(
            category=category,
            sku="R2-1",
            price="1000.00",
            stock=1,
            main_image=SimpleUploadedFile("main.jpg", b"main", content_type="image/jpeg"),
        )
        ProductImage.objects.create(
            product=product,
            image=SimpleUploadedFile("gal.jpg", b"gal", content_type="image/jpeg"),
            sort_order=0,
        )

        names = {product.main_image.name, product.gallery_images.get().image.name}
        product.delete()

        deleted_paths = {call.args[0] for call in delete_mock.call_args_list}
        self.assertTrue(names.issubset(deleted_paths))

    @patch("apps.core.r2_media.delete_file_from_r2")
    def test_product_main_image_replace_deletes_old(self, delete_mock) -> None:
        category = Category.objects.create(is_active=True)
        category.set_current_language("sr")
        category.name = "Kat"
        category.slug = "kat-replace"
        category.save()

        product = Product.objects.create(
            category=category,
            sku="R2-2",
            price="1000.00",
            stock=1,
            main_image=SimpleUploadedFile("old.jpg", b"old", content_type="image/jpeg"),
        )
        old_name = product.main_image.name

        product.main_image = SimpleUploadedFile("new.jpg", b"new", content_type="image/jpeg")
        product.save()

        self.assertIn(old_name, [c.args[0] for c in delete_mock.call_args_list])

    @patch("apps.core.r2_media.delete_file_from_r2")
    def test_gallery_image_delete(self, delete_mock) -> None:
        category = Category.objects.create(is_active=True)
        category.set_current_language("sr")
        category.name = "Kat"
        category.slug = "kat-gal"
        category.save()

        product = Product.objects.create(
            category=category,
            sku="R2-3",
            price="1000.00",
            stock=1,
        )
        row = ProductImage.objects.create(
            product=product,
            image=SimpleUploadedFile("g1.jpg", b"g1", content_type="image/jpeg"),
            sort_order=0,
        )
        path = row.image.name
        row.delete()
        delete_mock.assert_called_with(path)
