from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.fields import MoneyField


class OrderStatus(models.TextChoices):
    PENDING = "pending", _("Pending")
    CONFIRMED = "confirmed", _("Confirmed")
    PROCESSING = "processing", _("Processing")
    SHIPPED = "shipped", _("Shipped")
    DELIVERED = "delivered", _("Delivered")
    CANCELLED = "cancelled", _("Cancelled")


class PaymentMethod(models.TextChoices):
    COD = "cod", _("Cash on delivery")


class Order(models.Model):
    order_number = models.CharField(max_length=32, unique=True, db_index=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )
    guest_email = models.EmailField(
        help_text=_("Used for guest orders and order tracking."),
    )

    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=32)

    shipping_street = models.CharField(max_length=255)
    shipping_city_name = models.CharField(
        max_length=120,
        help_text=_("City name as entered by customer."),
    )
    shipping_postal_code = models.CharField(max_length=20)
    shipping_city = models.ForeignKey(
        "shipping.City",
        on_delete=models.PROTECT,
        related_name="orders",
    )

    billing_street = models.CharField(max_length=255)
    billing_city_name = models.CharField(max_length=120)
    billing_postal_code = models.CharField(max_length=20)

    order_notes = models.TextField(
        help_text=_("Required at checkout — delivery instructions."),
    )
    delivery_date = models.DateField(null=True, blank=True)
    flexible_delivery = models.BooleanField(default=False)

    shipping_method = models.ForeignKey(
        "shipping.ShippingMethod",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )
    shipping_price = MoneyField(default=0)

    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.COD,
    )
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
        db_index=True,
    )

    subtotal = MoneyField(default=0)
    total = MoneyField(default=0)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("order")
        verbose_name_plural = _("orders")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["guest_email"]),
            models.Index(fields=["user", "created_at"]),
        ]

    def __str__(self) -> str:
        return self.order_number

    @property
    def is_guest_order(self) -> bool:
        return self.user_id is None

    @property
    def customer_email(self) -> str:
        if self.user_id and self.user.email:
            return self.user.email
        return self.guest_email

    @property
    def customer_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_items",
    )
    product_name = models.CharField(max_length=255)
    sku = models.CharField(max_length=64)
    unit_price = MoneyField(validators=[MinValueValidator(Decimal("0"))])
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = _("order item")
        verbose_name_plural = _("order items")
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["product"]),
        ]

    def __str__(self) -> str:
        return f"{self.sku} x {self.quantity}"

    @property
    def line_total(self) -> Decimal:
        return self.unit_price * self.quantity
