from django.db import migrations, models


def copy_shipping_method_text(apps, schema_editor):
    ShippingMethod = apps.get_model("shipping", "ShippingMethod")
    for row in ShippingMethod.objects.all().iterator():
        row.name_sr = row.name
        row.description_sr = row.description or ""
        row.save(update_fields=["name_sr", "description_sr"])


class Migration(migrations.Migration):
    dependencies = [
        ("shipping", "0002_alter_city_is_active_alter_city_name_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="shippingmethod",
            name="name_sr",
            field=models.CharField(default="", max_length=120, verbose_name="Name (Serbian)"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="shippingmethod",
            name="name_en",
            field=models.CharField(blank=True, max_length=120, verbose_name="Name (English)"),
        ),
        migrations.AddField(
            model_name="shippingmethod",
            name="description_sr",
            field=models.TextField(blank=True, verbose_name="Description (Serbian)"),
        ),
        migrations.AddField(
            model_name="shippingmethod",
            name="description_en",
            field=models.TextField(blank=True, verbose_name="Description (English)"),
        ),
        migrations.RunPython(copy_shipping_method_text, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="shippingmethod",
            name="name",
        ),
        migrations.RemoveField(
            model_name="shippingmethod",
            name="description",
        ),
    ]
