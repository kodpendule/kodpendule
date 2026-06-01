from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Shop customer / staff user. Email is required at registration."""

    email = models.EmailField(_("email address"), blank=False, null=True, unique=True)

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        indexes = [
            models.Index(fields=["email"]),
        ]

    def __str__(self) -> str:
        return self.get_full_name() or self.username


class CustomerContact(models.Model):
    """
    Archived shop customer (one row per email).

    Filled on registration and checkout; guest and registered buyers with the
    same email share a single record.
    """

    email = models.EmailField(_("Email"), unique=True, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="customer_contacts",
        verbose_name=_("User account"),
    )
    first_name = models.CharField(_("First name"), max_length=120, blank=True)
    last_name = models.CharField(_("Last name"), max_length=120, blank=True)
    phone = models.CharField(_("Phone"), max_length=32, blank=True)
    delivery_street = models.CharField(_("Delivery street"), max_length=255, blank=True)
    delivery_city_name = models.CharField(_("Delivery city"), max_length=120, blank=True)
    order_count = models.PositiveIntegerField(_("Orders placed"), default=0)
    registered_at = models.DateTimeField(_("Registered at"), null=True, blank=True)
    first_seen_at = models.DateTimeField(_("First seen"), auto_now_add=True)
    last_seen_at = models.DateTimeField(_("Last activity"), auto_now=True)

    class Meta:
        verbose_name = _("customer contact")
        verbose_name_plural = _("customer contacts")
        ordering = ["-last_seen_at"]

    def __str__(self) -> str:
        return self.email

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()


class CustomerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    phone = models.CharField(_("Phone"), max_length=32, blank=True)

    class Meta:
        verbose_name = _("customer profile")
        verbose_name_plural = _("customer profiles")

    def __str__(self) -> str:
        return f"Profile: {self.user}"
