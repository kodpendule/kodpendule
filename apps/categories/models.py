from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields

class Category(TranslatableModel):
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name=_("Parent"),
    )
    image = models.ImageField(_("Image"), upload_to="categories/", blank=True)
    is_active = models.BooleanField(_("Active"), default=True)
    sort_order = models.PositiveIntegerField(_("Sort order"), default=0)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    translations = TranslatedFields(
        name=models.CharField(_("Name"), max_length=200),
        slug=models.SlugField(_("Slug"), max_length=220, unique=True),
        description=models.TextField(_("Description"), blank=True),
        meta_title=models.CharField(_("Meta title"), max_length=70, blank=True),
        meta_description=models.CharField(_("Meta description"), max_length=160, blank=True),
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

    def get_absolute_url(self) -> str:
        from apps.core.slugs import localized_slug

        slug = localized_slug(self)
        if not slug:
            return reverse("categories:list")
        return reverse("categories:detail", kwargs={"slug": slug})
