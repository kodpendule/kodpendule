from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields

from apps.core.fields import MoneyField


class Product(TranslatableModel):
    category = models.ForeignKey(
        "categories.Category",
        on_delete=models.PROTECT,
        related_name="products",
    )
    sku = models.CharField(max_length=64, unique=True, db_index=True)
    price = MoneyField(validators=[MinValueValidator(Decimal("0"))])
    discount_price = MoneyField(
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0"))],
    )
    main_image = models.ImageField(upload_to="products/", blank=True)
    stock = models.PositiveIntegerField(default=0)
    minimum_stock_alert = models.PositiveIntegerField(default=5)
    is_active = models.BooleanField(default=True, db_index=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    is_recommended = models.BooleanField(default=False, db_index=True)
    is_on_sale = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    translations = TranslatedFields(
        name=models.CharField(max_length=255),
        slug=models.SlugField(max_length=270, unique=True),
        short_description=models.CharField(max_length=500, blank=True),
        description=models.TextField(blank=True),
        meta_title=models.CharField(max_length=70, blank=True),
        meta_description=models.CharField(max_length=160, blank=True),
    )

    class Meta:
        verbose_name = _("product")
        verbose_name_plural = _("products")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["category", "is_active"]),
            models.Index(fields=["is_featured", "is_active"]),
            models.Index(fields=["is_recommended", "is_active"]),
            models.Index(fields=["is_on_sale", "is_active"]),
            models.Index(fields=["stock"]),
        ]

    def __str__(self) -> str:
        return self.safe_translation_getter("name", any_language=True) or self.sku

    @property
    def effective_price(self) -> Decimal:
        if self.discount_price is not None and self.discount_price < self.price:
            return self.discount_price
        return self.price

    @property
    def is_low_stock(self) -> bool:
        return self.stock <= self.minimum_stock_alert

    @property
    def has_discount(self) -> bool:
        return (
            self.discount_price is not None
            and self.discount_price < self.price
        )


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="gallery_images",
    )
    image = models.ImageField(upload_to="products/gallery/")
    alt_text = models.CharField(max_length=255, blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _("product image")
        verbose_name_plural = _("product images")
        ordering = ["sort_order", "id"]
        indexes = [
            models.Index(fields=["product", "sort_order"]),
        ]

    def __str__(self) -> str:
        return f"Image for {self.product_id} (#{self.pk})"
