from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Shop customer / staff user. Email optional but unique when set."""

    email = models.EmailField(_("email address"), blank=True, null=True, unique=True)

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


class AddressType(models.TextChoices):
    SHIPPING = "shipping", _("Shipping")
    BILLING = "billing", _("Billing")


class Address(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="addresses",
        verbose_name=_("User"),
    )
    address_type = models.CharField(
        _("Address type"),
        max_length=20,
        choices=AddressType.choices,
        default=AddressType.SHIPPING,
    )
    label = models.CharField(_("Label"), max_length=64, blank=True)
    street_line_1 = models.CharField(_("Street line 1"), max_length=255)
    street_line_2 = models.CharField(_("Street line 2"), max_length=255, blank=True)
    city = models.CharField(_("City"), max_length=120)
    postal_code = models.CharField(_("Postal code"), max_length=20)
    is_default = models.BooleanField(_("Default address"), default=False)

    class Meta:
        verbose_name = _("address")
        verbose_name_plural = _("addresses")
        ordering = ["-is_default", "id"]
        indexes = [
            models.Index(fields=["user", "address_type"]),
        ]

    def __str__(self) -> str:
        return f"{self.get_address_type_display()} — {self.city}"
