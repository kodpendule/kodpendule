from django.db import migrations, models
from django.utils import timezone


def set_default_delivery_dates(apps, schema_editor):
    Order = apps.get_model("orders", "Order")
    for order in Order.objects.filter(requested_delivery_date__isnull=True):
        created = order.created_at
        if timezone.is_aware(created):
            created = timezone.localtime(created)
        order.requested_delivery_date = created.date()
        order.save(update_fields=["requested_delivery_date"])


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0005_order_is_new"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="requested_delivery_date",
            field=models.DateField(
                help_text="Customer's preferred delivery date from checkout.",
                null=True,
                verbose_name="Requested delivery date",
            ),
        ),
        migrations.RunPython(set_default_delivery_dates, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="order",
            name="requested_delivery_date",
            field=models.DateField(
                help_text="Customer's preferred delivery date from checkout.",
                verbose_name="Requested delivery date",
            ),
        ),
    ]
