from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_checkoutsettings"),
        ("shipping", "0006_city_promo_delivery_rules"),
    ]

    operations = [
        migrations.DeleteModel(
            name="CheckoutSettings",
        ),
    ]
