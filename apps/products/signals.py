from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver

from apps.core.r2_media import delete_model_file_field
from apps.products.models import Product, ProductImage


@receiver(pre_delete, sender=Product)
def delete_product_media(sender, instance, **kwargs):
    delete_model_file_field(instance.main_image)
    for gallery_row in instance.gallery_images.all():
        delete_model_file_field(gallery_row.image)


@receiver(pre_save, sender=Product)
def cleanup_old_product_main_image(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old = Product.objects.get(pk=instance.pk)
    except Product.DoesNotExist:
        return
    if old.main_image and old.main_image != instance.main_image:
        delete_model_file_field(old.main_image)


@receiver(pre_delete, sender=ProductImage)
def delete_product_gallery_image(sender, instance, **kwargs):
    delete_model_file_field(instance.image)


@receiver(pre_save, sender=ProductImage)
def cleanup_old_product_gallery_image(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old = ProductImage.objects.get(pk=instance.pk)
    except ProductImage.DoesNotExist:
        return
    if old.image and old.image != instance.image:
        delete_model_file_field(old.image)
