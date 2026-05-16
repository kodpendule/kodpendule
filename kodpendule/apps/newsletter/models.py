from django.db import models
from django.utils.translation import gettext_lazy as _


class SubscriberSource(models.TextChoices):
    CHECKOUT = "checkout", _("Checkout")
    FOOTER = "footer", _("Footer form")
    IMPORT = "import", _("Admin import")
    MANUAL = "manual", _("Manual")


class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    source = models.CharField(
        max_length=20,
        choices=SubscriberSource.choices,
        default=SubscriberSource.MANUAL,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("subscriber")
        verbose_name_plural = _("subscribers")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_active", "created_at"]),
        ]

    def __str__(self) -> str:
        return self.email


class CampaignStatus(models.TextChoices):
    DRAFT = "draft", _("Draft")
    SENT = "sent", _("Sent")


class EmailCampaign(models.Model):
    """Prepared for future promotional sends (no Celery in v1)."""

    subject = models.CharField(max_length=255)
    body = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=CampaignStatus.choices,
        default=CampaignStatus.DRAFT,
    )
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("email campaign")
        verbose_name_plural = _("email campaigns")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.subject
