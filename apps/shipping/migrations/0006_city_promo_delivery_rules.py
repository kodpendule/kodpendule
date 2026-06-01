# Generated manually — per-city promotional delivery rules

from django.db import migrations, models

import apps.core.fields


def copy_global_checkout_settings(apps, schema_editor):
    CheckoutSettings = apps.get_model("core", "CheckoutSettings")
    City = apps.get_model("shipping", "City")
    try:
        settings = CheckoutSettings.objects.get(pk=1)
    except CheckoutSettings.DoesNotExist:
        return
    if settings.free_shipping_threshold is None:
        return
    City.objects.filter(is_active=True).update(
        promo_cart_threshold=settings.free_shipping_threshold,
        promo_shipping_mode=settings.threshold_shipping_mode,
        promo_discounted_shipping_price=settings.discounted_shipping_price,
    )


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_checkoutsettings"),
        ("shipping", "0005_remove_legacy_checkout_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="city",
            name="promo_cart_threshold",
            field=apps.core.fields.MoneyField(
                blank=True,
                decimal_places=2,
                help_text="When the cart subtotal is at or above this amount (RSD), the promotional delivery rule below applies. Leave empty to disable.",
                max_digits=12,
                null=True,
                verbose_name="Cart total threshold",
            ),
        ),
        migrations.AddField(
            model_name="city",
            name="promo_discounted_shipping_price",
            field=apps.core.fields.MoneyField(
                blank=True,
                decimal_places=2,
                help_text="Used when threshold is reached and mode is “Discounted shipping price”. Leave empty if you only use free shipping.",
                max_digits=12,
                null=True,
                verbose_name="Discounted shipping price",
            ),
        ),
        migrations.AddField(
            model_name="city",
            name="promo_shipping_mode",
            field=models.CharField(
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
        migrations.RunPython(copy_global_checkout_settings, migrations.RunPython.noop),
    ]
