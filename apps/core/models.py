"""Singleton site configuration (pk=1)."""

from django.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields


class SiteSettings(TranslatableModel):
    """Singleton site configuration (pk=1)."""

    translations = TranslatedFields(
        site_name=models.CharField(_("Site name"), max_length=120, default="Kod Pendule"),
        default_meta_title=models.CharField(_("Default meta title"), max_length=70, blank=True),
        default_meta_description=models.CharField(
            _("Default meta description"),
            max_length=160,
            blank=True,
        ),
    )

    class Meta:
        verbose_name = _("site settings")
        verbose_name_plural = _("site settings")

    def save(self, *args, **kwargs) -> None:
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) -> None:
        pass

    @classmethod
    def load(cls) -> "SiteSettings":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class FooterSettings(TranslatableModel):
    """Singleton footer / contact block (pk=1)."""

    phone = models.CharField(_("Phone"), max_length=32, blank=True)
    email = models.EmailField(_("Email"), blank=True)

    translations = TranslatedFields(
        address=models.TextField(_("Address"), blank=True),
        working_hours=models.TextField(_("Working hours"), blank=True),
    )

    class Meta:
        verbose_name = _("footer settings")
        verbose_name_plural = _("footer settings")

    def save(self, *args, **kwargs) -> None:
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls) -> "FooterSettings":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
