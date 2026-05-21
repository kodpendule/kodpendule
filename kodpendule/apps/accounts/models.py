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


class CustomerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    phone = models.CharField(_("Phone"), max_length=32, blank=True)
    newsletter_opt_in = models.BooleanField(_("Newsletter opt-in"), default=False)

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
