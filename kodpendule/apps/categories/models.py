from django.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields


class Category(TranslatableModel):
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )
    image = models.ImageField(upload_to="categories/", blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    translations = TranslatedFields(
        name=models.CharField(max_length=200),
        slug=models.SlugField(max_length=220, unique=True),
        description=models.TextField(blank=True),
        meta_title=models.CharField(max_length=70, blank=True),
        meta_description=models.CharField(max_length=160, blank=True),
    )

    class Meta:
        verbose_name = _("category")
        verbose_name_plural = _("categories")
        ordering = ["sort_order", "pk"]
        indexes = [
            models.Index(fields=["is_active", "sort_order"]),
            models.Index(fields=["parent"]),
        ]

    def __str__(self) -> str:
        return self.safe_translation_getter("name", any_language=True) or f"Category #{self.pk}"
