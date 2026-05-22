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

    def __str__(self) -> str:
        return "Site settings"


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

    def delete(self, *args, **kwargs) -> None:
        pass

    @classmethod
    def load(cls) -> "FooterSettings":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self) -> str:
        return "Footer settings"


class SocialPlatform(models.TextChoices):
    FACEBOOK = "facebook", "Facebook"
    INSTAGRAM = "instagram", "Instagram"
    TWITTER = "twitter", "X (Twitter)"
    YOUTUBE = "youtube", "YouTube"
    TIKTOK = "tiktok", "TikTok"
    LINKEDIN = "linkedin", "LinkedIn"
    OTHER = "other", _("Other")


class SocialLink(models.Model):
    platform = models.CharField(_("Platform"), max_length=32, choices=SocialPlatform.choices)
    url = models.URLField(_("URL"))
    sort_order = models.PositiveIntegerField(_("Sort order"), default=0)
    is_active = models.BooleanField(_("Active"), default=True)

    class Meta:
        verbose_name = _("social link")
        verbose_name_plural = _("social links")
        ordering = ["sort_order", "id"]

    def __str__(self) -> str:
        return f"{self.get_platform_display()}"


class HeroBanner(TranslatableModel):
    image = models.ImageField(_("Image"), upload_to="banners/")
    link_url = models.CharField(_("Link URL"), max_length=500, blank=True)
    sort_order = models.PositiveIntegerField(_("Sort order"), default=0)
    is_active = models.BooleanField(_("Active"), default=True)

    translations = TranslatedFields(
        title=models.CharField(_("Title"), max_length=200, blank=True),
        subtitle=models.CharField(_("Subtitle"), max_length=300, blank=True),
    )

    class Meta:
        verbose_name = _("hero banner")
        verbose_name_plural = _("hero banners")
        ordering = ["sort_order", "id"]
        indexes = [
            models.Index(fields=["is_active", "sort_order"]),
        ]

    def __str__(self) -> str:
        return self.safe_translation_getter("title", any_language=True) or f"Banner #{self.pk}"


class PromoPlacement(models.TextChoices):
    HOMEPAGE_MIDDLE = "homepage_middle", _("Homepage middle")
    HOMEPAGE_BOTTOM = "homepage_bottom", _("Homepage bottom")


class PromoSection(TranslatableModel):
    image = models.ImageField(_("Image"), upload_to="promos/", blank=True)
    link_url = models.CharField(_("Link URL"), max_length=500, blank=True)
    placement = models.CharField(
        _("Placement"),
        max_length=32,
        choices=PromoPlacement.choices,
        default=PromoPlacement.HOMEPAGE_MIDDLE,
    )
    sort_order = models.PositiveIntegerField(_("Sort order"), default=0)
    is_active = models.BooleanField(_("Active"), default=True)

    translations = TranslatedFields(
        title=models.CharField(_("Title"), max_length=200, blank=True),
        body=models.TextField(_("Body"), blank=True),
    )

    class Meta:
        verbose_name = _("promo section")
        verbose_name_plural = _("promo sections")
        ordering = ["sort_order", "id"]
        indexes = [
            models.Index(fields=["placement", "is_active", "sort_order"]),
        ]

    def __str__(self) -> str:
        return self.safe_translation_getter("title", any_language=True) or f"Promo #{self.pk}"


class HomepageSectionType(models.TextChoices):
    FEATURED = "featured", _("Featured products")
    RECOMMENDED = "recommended", _("Recommended products")
    SALE = "sale", _("Sale / action products")


class HomepageSection(models.Model):
    """Controls which product blocks appear on the homepage."""

    section_type = models.CharField(
        _("Section type"),
        max_length=20,
        choices=HomepageSectionType.choices,
        unique=True,
    )
    is_active = models.BooleanField(_("Active"), default=True)
    max_products = models.PositiveSmallIntegerField(_("Max products"), default=8)

    class Meta:
        verbose_name = _("homepage section")
        verbose_name_plural = _("homepage sections")
        ordering = ["section_type"]

    def __str__(self) -> str:
        return self.get_section_type_display()
