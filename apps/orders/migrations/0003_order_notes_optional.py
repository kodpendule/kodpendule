from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0002_alter_order_billing_city_name_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="order_notes",
            field=models.TextField(
                blank=True,
                help_text="Optional note from checkout.",
                verbose_name="Order notes",
            ),
        ),
    ]
