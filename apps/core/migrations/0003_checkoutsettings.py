# Generated manually for checkout settings singleton

from django.db import migrations, models

import apps.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_remove_legacy_cms"),
    ]

    operations = [
        migrations.CreateModel(
            name="CheckoutSettings",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "free_shipping_threshold",
                    apps.core.fields.MoneyField(
                        blank=True,
                        decimal_places=2,
                        help_text="When the cart subtotal is at or above this amount (RSD), the threshold shipping rule below applies. Leave empty to disable.",
                        max_digits=12,
                        null=True,
                        verbose_name="Free shipping threshold",
                    ),
                ),
                (
                    "threshold_shipping_mode",
                    models.CharField(
                        choices=[
                            ("free", "Free shipping"),
                            ("discounted", "Discounted shipping price"),
                        ],
                        default="free",
                        help_text="Choose free delivery or the discounted shipping price configured below.",
                        max_length=20,
                        verbose_name="When threshold is reached",
                    ),
                ),
                (
                    "discounted_shipping_price",
                    apps.core.fields.MoneyField(
                        blank=True,
                        decimal_places=2,
                        help_text="Used when threshold is reached and mode is “Discounted shipping price”. Leave empty if you only use free shipping.",
                        max_digits=12,
                        null=True,
                        verbose_name="Discounted shipping price",
                    ),
                ),
            ],
            options={
                "verbose_name": "checkout settings",
                "verbose_name_plural": "checkout settings",
            },
        ),
    ]
