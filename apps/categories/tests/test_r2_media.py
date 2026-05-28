from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from apps.categories.models import Category


@override_settings(USE_R2=True)
class CategoryR2MediaDeletionTests(TestCase):
    @patch("apps.core.r2_media.delete_file_from_r2")
    def test_category_delete_removes_image(self, delete_mock) -> None:
        category = Category.objects.create(is_active=True)
        category.set_current_language("sr")
        category.name = "Satovi"
        category.slug = "satovi"
        category.save()
        category.image = SimpleUploadedFile("cat.jpg", b"img", content_type="image/jpeg")
        category.save()

        path = category.image.name
        category.delete()

        delete_mock.assert_any_call(path)

    @patch("apps.core.r2_media.delete_file_from_r2")
    def test_category_image_replace_deletes_old(self, delete_mock) -> None:
        category = Category.objects.create(is_active=True)
        category.set_current_language("sr")
        category.name = "Narukvice"
        category.slug = "narukvice"
        category.save()
        category.image = SimpleUploadedFile("old.jpg", b"old", content_type="image/jpeg")
        category.save()
        old_name = category.image.name

        category.image = SimpleUploadedFile("new.jpg", b"new", content_type="image/jpeg")
        category.save()

        self.assertIn(old_name, [c.args[0] for c in delete_mock.call_args_list])
