from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver

from apps.categories.models import Category
from apps.core.r2_media import delete_model_file_field


@receiver(pre_delete, sender=Category)
def delete_category_image(sender, instance, **kwargs):
    delete_model_file_field(instance.image)


@receiver(pre_save, sender=Category)
def cleanup_old_category_image(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old = Category.objects.get(pk=instance.pk)
    except Category.DoesNotExist:
        return
    if old.image and old.image != instance.image:
        delete_model_file_field(old.image)
